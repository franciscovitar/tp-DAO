"""Pruebas de la carga opcional de una biblioteca de demostración."""

from datetime import date, timedelta
from pathlib import Path
import subprocess
import sys

import pytest

import cargar_datos_demo as modulo_demo
from cargar_datos_demo import ajustar_transito_demo, cargar_datos_demo
from datos.base_datos import DatabaseSingleton, conectar
from datos.ejemplares import agregar_ejemplar, buscar_ejemplar_por_codigo
from datos.libros import agregar_libro
from datos.prestamos import registrar_devolucion, registrar_prestamo_local
from datos.remitos import listar_historial_remito
from datos.reportes import movimientos_y_tiempo_promedio_transito, prestamos_vencidos
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
                       "ejemplares": 20, "reservas": 3, "prestamos": 5,
                       "remitos": 2}

    conexion = conectar(base_temporal)
    assert _cantidades(conexion) == {
        "sedes": 3, "socios": 8, "libros": 10, "ejemplares": 20,
        "reservas": 3, "prestamos": 5, "remitos": 2, "historial_remito": 5,
    }
    assert dict(conexion.execute(
        "SELECT estado, COUNT(*) FROM reservas GROUP BY estado"
    ).fetchall()) == {"ACTIVA": 1, "CUMPLIDA": 1, "CANCELADA": 1}
    assert dict(conexion.execute(
        "SELECT estado, COUNT(*) FROM prestamos GROUP BY estado"
    ).fetchall()) == {"ACTIVO": 3, "DEVUELTO": 1, "SOLICITADO": 1}

    assert buscar_ejemplar_por_codigo("DEMO-C-01", base_temporal)[5] == "RESERVADO"
    assert buscar_ejemplar_por_codigo("DEMO-N-01", base_temporal)[5] == "PRESTADO"
    assert buscar_ejemplar_por_codigo("DEMO-C-02", base_temporal)[5] == "DISPONIBLE"
    danado = buscar_ejemplar_por_codigo("DEMO-S-02", base_temporal)
    assert danado[5:7] == ("BAJA", "DANADO")
    assert buscar_ejemplar_por_codigo("DEMO-C-03", base_temporal)[5] == "RESERVADO"
    traslado = buscar_ejemplar_por_codigo("DEMO-N-03", base_temporal)
    assert traslado[5] == "PRESTADO"
    assert traslado[3] != traslado[4]
    assert buscar_ejemplar_por_codigo("DEMO-C-06", base_temporal)[5] == "PRESTADO"

    vencidos = prestamos_vencidos(base_temporal)
    assert len(vencidos) == 1
    assert vencidos[0][1:5] == ("49000008", "Nicolás Herrera", "1984", "DEMO-C-06")
    assert vencidos[0][5] == (date.today() - timedelta(days=7)).isoformat()
    fechas_vencido = conexion.execute("""
        SELECT fecha_solicitud, fecha_inicio, fecha_vencimiento, estado
        FROM prestamos WHERE id = ?
    """, (vencidos[0][0],)).fetchone()
    assert fechas_vencido == (
        (date.today() - timedelta(days=21)).isoformat(),
        (date.today() - timedelta(days=21)).isoformat(),
        (date.today() - timedelta(days=7)).isoformat(), "ACTIVO"
    )

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
    assert movimientos_y_tiempo_promedio_transito(base_temporal)[
        "horas_promedio_transito"
    ] == pytest.approx(4.5, abs=0.0001)

    fechas = conexion.execute("""
        SELECT r.fecha_creacion, r.fecha_despacho, r.fecha_recepcion, p.fecha_solicitud
        FROM remitos r JOIN prestamos p ON p.id = r.prestamo_id
        WHERE r.numero = 'DEMO-IDA-002'
    """).fetchone()
    assert fechas[3] <= fechas[0][:10]
    assert fechas[0] < fechas[1] < fechas[2]
    eventos = listar_historial_remito(remitos[1][0], base_temporal)
    assert [fila[1] for fila in eventos] == sorted(fila[1] for fila in eventos)
    assert eventos[0][1] == fechas[0]
    assert eventos[1][1] == fechas[1]
    assert fechas[1] < eventos[2][1] < fechas[2]
    assert eventos[3][1] == fechas[2]


def test_carga_demo_es_idempotente(base_temporal):
    cargar_datos_demo(base_temporal)
    conexion = conectar(base_temporal)
    primera = _cantidades(conexion)
    fechas_antes = conexion.execute("""
        SELECT fecha_creacion, fecha_despacho, fecha_recepcion
        FROM remitos WHERE numero = 'DEMO-IDA-002'
    """).fetchone()
    assert cargar_datos_demo(base_temporal) == {
        "sedes": 0, "socios": 0, "libros": 0, "ejemplares": 0,
        "reservas": 0, "prestamos": 0, "remitos": 0,
    }
    assert _cantidades(conectar(base_temporal)) == primera
    assert conexion.execute("""
        SELECT fecha_creacion, fecha_despacho, fecha_recepcion
        FROM remitos WHERE numero = 'DEMO-IDA-002'
    """).fetchone() == fechas_antes


def test_recarga_demo_antigua_agrega_solo_prestamo_vencido(base_temporal, monkeypatch):
    # Carga equivalente a la versión anterior, sin el caso vencido.
    with monkeypatch.context() as anterior:
        anterior.setattr(modulo_demo, "_crear_prestamo_vencido_demo",
                         lambda *argumentos: False)
        creados = cargar_datos_demo(base_temporal)
    assert creados["prestamos"] == 4
    conexion = conectar(base_temporal)
    ejemplares_antes = _cantidades(conexion)["ejemplares"]

    segunda = cargar_datos_demo(base_temporal)
    assert segunda == {"sedes": 0, "socios": 0, "libros": 0,
                       "ejemplares": 0, "reservas": 0, "prestamos": 1,
                       "remitos": 0}
    assert _cantidades(conexion)["ejemplares"] == ejemplares_antes
    assert len(prestamos_vencidos(base_temporal)) == 1
    assert cargar_datos_demo(base_temporal)["prestamos"] == 0
    assert len(prestamos_vencidos(base_temporal)) == 1


def test_recarga_demo_respeta_ejemplar_usado_por_el_usuario(base_temporal, monkeypatch):
    with monkeypatch.context() as anterior:
        anterior.setattr(modulo_demo, "_crear_prestamo_vencido_demo",
                         lambda *argumentos: False)
        cargar_datos_demo(base_temporal)

    conexion = conectar(base_temporal)
    socio_id = conexion.execute("""
        SELECT id FROM socios WHERE dni = '49000008'
    """).fetchone()[0]
    ejemplar_id, sede_id = conexion.execute("""
        SELECT id, sede_pertenencia_id FROM ejemplares WHERE codigo = 'DEMO-C-06'
    """).fetchone()
    ok, prestamo_id = registrar_prestamo_local(
        socio_id, ejemplar_id, sede_id, nombre_archivo=base_temporal
    )
    assert ok
    assert registrar_devolucion(prestamo_id, nombre_archivo=base_temporal)[0]
    prestamos_antes = _cantidades(conexion)["prestamos"]

    assert cargar_datos_demo(base_temporal)["prestamos"] == 0
    assert _cantidades(conexion)["prestamos"] == prestamos_antes
    assert prestamos_vencidos(base_temporal) == []
    assert buscar_ejemplar_por_codigo("DEMO-C-06", base_temporal)[5] == "DISPONIBLE"


def test_ajuste_optativo_repara_solo_remito_demo_ya_cargado(base_temporal):
    cargar_datos_demo(base_temporal)
    conexion = conectar(base_temporal)
    id_remito, recepcion = conexion.execute("""
        SELECT id, fecha_recepcion FROM remitos WHERE numero = 'DEMO-IDA-002'
    """).fetchone()
    otro_antes = conexion.execute("""
        SELECT * FROM remitos WHERE numero = 'DEMO-IDA-001'
    """).fetchone()
    prestamos_otros = conexion.execute("""
        SELECT * FROM prestamos WHERE id NOT IN (
            SELECT prestamo_id FROM remitos WHERE id = ?
        ) ORDER BY id
    """, (id_remito,)).fetchall()

    # Simula la biblioteca de una versión anterior, con todos los eventos
    # generados durante el mismo segundo.
    conexion.execute("""
        UPDATE remitos SET fecha_creacion = ?, fecha_despacho = ?
        WHERE id = ?
    """, (recepcion, recepcion, id_remito))
    conexion.execute("""
        UPDATE historial_remito SET fecha_hora = ? WHERE remito_id = ?
    """, (recepcion, id_remito))
    conexion.commit()
    assert movimientos_y_tiempo_promedio_transito(base_temporal)[
        "horas_promedio_transito"
    ] == pytest.approx(0)

    assert ajustar_transito_demo(base_temporal) is True
    assert movimientos_y_tiempo_promedio_transito(base_temporal)[
        "horas_promedio_transito"
    ] == pytest.approx(4.5, abs=0.0001)
    assert ajustar_transito_demo(base_temporal) is False
    assert conexion.execute("""
        SELECT * FROM remitos WHERE numero = 'DEMO-IDA-001'
    """).fetchone() == otro_antes
    assert conexion.execute("""
        SELECT * FROM prestamos WHERE id NOT IN (
            SELECT prestamo_id FROM remitos WHERE id = ?
        ) ORDER BY id
    """, (id_remito,)).fetchall() == prestamos_otros


def test_ajuste_optativo_respeta_tiempos_ya_registrados(base_temporal):
    cargar_datos_demo(base_temporal)
    conexion = conectar(base_temporal)
    remito_antes = conexion.execute("""
        SELECT * FROM remitos WHERE numero = 'DEMO-IDA-002'
    """).fetchone()
    historial_antes = conexion.execute("""
        SELECT * FROM historial_remito WHERE remito_id = ? ORDER BY id
    """, (remito_antes[0],)).fetchall()

    assert ajustar_transito_demo(base_temporal) is False
    assert conexion.execute("""
        SELECT * FROM remitos WHERE numero = 'DEMO-IDA-002'
    """).fetchone() == remito_antes
    assert conexion.execute("""
        SELECT * FROM historial_remito WHERE remito_id = ? ORDER BY id
    """, (remito_antes[0],)).fetchall() == historial_antes


def test_ajuste_optativo_no_modifica_remito_demo_con_historial_editado(base_temporal):
    cargar_datos_demo(base_temporal)
    conexion = conectar(base_temporal)
    remito_id, recepcion = conexion.execute("""
        SELECT id, fecha_recepcion FROM remitos WHERE numero = 'DEMO-IDA-002'
    """).fetchone()
    conexion.execute("""
        UPDATE remitos SET fecha_creacion = ?, fecha_despacho = ? WHERE id = ?
    """, (recepcion, recepcion, remito_id))
    # El usuario agregó un estado; no se reescribe un historial intervenido.
    conexion.execute("""
        INSERT INTO historial_remito (remito_id, estado, fecha_hora)
        VALUES (?, 'RECIBIDO', ?)
    """, (remito_id, recepcion))
    conexion.commit()

    assert ajustar_transito_demo(base_temporal) is False
    assert conexion.execute("""
        SELECT fecha_despacho FROM remitos WHERE id = ?
    """, (remito_id,)).fetchone()[0] == recepcion


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


def test_comando_ajusta_remito_preexistente_con_opcion_explicita(tmp_path):
    nombre = str(tmp_path / "ejemplo.db")
    cargar_datos_demo(nombre)
    conexion = conectar(nombre)
    remito_id, recepcion = conexion.execute("""
        SELECT id, fecha_recepcion FROM remitos WHERE numero = 'DEMO-IDA-002'
    """).fetchone()
    conexion.execute("""
        UPDATE remitos SET fecha_creacion = ?, fecha_despacho = ? WHERE id = ?
    """, (recepcion, recepcion, remito_id))
    conexion.execute("""
        UPDATE historial_remito SET fecha_hora = ? WHERE remito_id = ?
    """, (recepcion, remito_id))
    conexion.commit()
    DatabaseSingleton().close_connection()

    script = Path(__file__).resolve().parents[1] / "cargar_datos_demo.py"
    resultado = subprocess.run(
        [sys.executable, str(script), "--bd", nombre, "--ajustar-traslado-demo"],
        cwd=tmp_path, capture_output=True, text=True, check=True,
    )

    assert "tránsito ficticio de 4 h 30 min" in resultado.stdout
    assert movimientos_y_tiempo_promedio_transito(nombre)[
        "horas_promedio_transito"
    ] == pytest.approx(4.5, abs=0.0001)
    assert not (tmp_path / "biblioteca.db").exists()
