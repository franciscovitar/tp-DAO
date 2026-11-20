"""Pruebas de la carga opcional de una biblioteca de demostración."""

from pathlib import Path
import subprocess
import sys

import pytest

from cargar_datos_demo import cargar_datos_demo
from datos.base_datos import DatabaseSingleton, conectar
from datos.ejemplares import agregar_ejemplar, buscar_ejemplar_por_codigo
from datos.libros import agregar_libro
from datos.remitos import listar_historial_remito
from datos.sedes import agregar_sede
from modelos.ejemplar import Ejemplar
from modelos.libro import Libro
from modelos.sede import Sede


@pytest.fixture
def base_temporal(tmp_path):
    nombre = str(tmp_path / "demo.db")
    yield nombre
    DatabaseSingleton().close_connection()


def _cantidades(conexion):
    tablas = ("sedes", "socios", "libros", "ejemplares",
              "reservas", "prestamos", "remitos", "historial_remito")
    return {
        tabla: conexion.execute(f"SELECT COUNT(*) FROM {tabla}").fetchone()[0]
        for tabla in tablas
    }


def test_carga_demo_crea_casos_para_mostrar(base_temporal):
    creados = cargar_datos_demo(base_temporal)
    assert creados == {"sedes": 3, "socios": 8, "libros": 10,
                       "ejemplares": 20, "reservas": 3, "prestamos": 4,
                       "remitos": 2}

    conexion = conectar(base_temporal)
    assert _cantidades(conexion) == {
        "sedes": 3, "socios": 8, "libros": 10, "ejemplares": 20,
        "reservas": 3, "prestamos": 4, "remitos": 2, "historial_remito": 5,
    }
    assert dict(conexion.execute(
        "SELECT estado, COUNT(*) FROM reservas GROUP BY estado"
    ).fetchall()) == {"ACTIVA": 1, "CUMPLIDA": 1, "CANCELADA": 1}
    assert dict(conexion.execute(
        "SELECT estado, COUNT(*) FROM prestamos GROUP BY estado"
    ).fetchall()) == {"ACTIVO": 2, "DEVUELTO": 1, "SOLICITADO": 1}

    assert buscar_ejemplar_por_codigo("DEMO-C-01", base_temporal)[5] == "RESERVADO"
    assert buscar_ejemplar_por_codigo("DEMO-N-01", base_temporal)[5] == "PRESTADO"
    assert buscar_ejemplar_por_codigo("DEMO-C-02", base_temporal)[5] == "DISPONIBLE"
    danado = buscar_ejemplar_por_codigo("DEMO-S-02", base_temporal)
    assert danado[5:7] == ("BAJA", "DANADO")
    assert buscar_ejemplar_por_codigo("DEMO-C-03", base_temporal)[5] == "RESERVADO"
    traslado = buscar_ejemplar_por_codigo("DEMO-N-03", base_temporal)
    assert traslado[5] == "PRESTADO"
    assert traslado[3] != traslado[4]

    remitos = conexion.execute(
        "SELECT id, numero, estado FROM remitos ORDER BY numero"
    ).fetchall()
    assert [(fila[1], fila[2]) for fila in remitos] == [
        ("DEMO-IDA-001", "PREPARADO"), ("DEMO-IDA-002", "RECIBIDO")
    ]
    assert [fila[0] for fila in listar_historial_remito(remitos[0][0], base_temporal)] == [
        "PREPARADO"
    ]
    assert [fila[0] for fila in listar_historial_remito(remitos[1][0], base_temporal)] == [
        "PREPARADO", "DESPACHADO", "EN_TRANSITO", "RECIBIDO"
    ]


def test_carga_demo_es_idempotente(base_temporal):
    cargar_datos_demo(base_temporal)
    primera = _cantidades(conectar(base_temporal))
    assert cargar_datos_demo(base_temporal) == {
        "sedes": 0, "socios": 0, "libros": 0, "ejemplares": 0,
        "reservas": 0, "prestamos": 0, "remitos": 0,
    }
    assert _cantidades(conectar(base_temporal)) == primera


def test_carga_demo_conserva_datos_existentes(base_temporal):
    from datos.base_datos import crear_tablas

    crear_tablas(base_temporal)
    sede_personal = Sede("Sede personal", "Colón 200", "", "", "")
    assert agregar_sede(sede_personal, base_temporal)
    libro_personal = Libro("9789501234567", "Libro del usuario", "Autor Propio", "", 2020)
    assert agregar_libro(libro_personal, base_temporal)
    ejemplar_personal = Ejemplar("PERSONAL-01", libro_personal, sede_personal)
    assert agregar_ejemplar(ejemplar_personal, base_temporal)

    cargar_datos_demo(base_temporal)
    assert buscar_ejemplar_por_codigo("PERSONAL-01", base_temporal)[5] == "DISPONIBLE"
    assert conectar(base_temporal).execute(
        "SELECT titulo FROM libros WHERE id = ?", (libro_personal.id,)
    ).fetchone()[0] == "Libro del usuario"
    assert _cantidades(conectar(base_temporal))["ejemplares"] == 21


def test_colision_codigo_no_altera_ejemplar_existente(base_temporal):
    from datos.base_datos import crear_tablas

    crear_tablas(base_temporal)
    sede_personal = Sede("Sede personal", "Colón 200", "", "", "")
    assert agregar_sede(sede_personal, base_temporal)
    libro_personal = Libro("9789501234567", "Libro del usuario", "Autor Propio", "", 2020)
    assert agregar_libro(libro_personal, base_temporal)
    ejemplar_personal = Ejemplar("DEMO-C-01", libro_personal, sede_personal)
    assert agregar_ejemplar(ejemplar_personal, base_temporal)

    cantidades = cargar_datos_demo(base_temporal)
    assert cantidades["ejemplares"] == 19
    assert cantidades["reservas"] == 2
    guardado = buscar_ejemplar_por_codigo("DEMO-C-01", base_temporal)
    assert guardado[2] == libro_personal.id
    assert guardado[5] == "DISPONIBLE"


def test_comando_bd_personalizada_no_crea_biblioteca_por_defecto(tmp_path):
    script = Path(__file__).resolve().parents[1] / "cargar_datos_demo.py"
    comando = [sys.executable, str(script), "--bd", "ejemplo.db"]

    primero = subprocess.run(comando, cwd=tmp_path, capture_output=True,
                            text=True, check=True)
    segundo = subprocess.run(comando, cwd=tmp_path, capture_output=True,
                            text=True, check=True)

    assert "20 nuevos" in primero.stdout
    assert "Los ejemplos ya estaban cargados" in segundo.stdout
    assert (tmp_path / "ejemplo.db").exists()
    assert not (tmp_path / "biblioteca.db").exists()
