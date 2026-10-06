import os

from datos.base_datos import crear_tablas, conectar
from datos.sedes import agregar_sede
from datos.socios import agregar_socio
from datos.libros import agregar_libro
from datos.ejemplares import agregar_ejemplar
from datos.prestamos import registrar_prestamo_local, solicitar_prestamo_interbibliotecario
from datos.remitos import crear_remito, cambiar_estado_remito
from datos.reportes import (
    prestamos_activos_y_material_en_transito,
    libros_mas_solicitados_interbibliotecarios,
    disponibilidad_catalogo_por_sede,
    movimientos_y_tiempo_promedio_transito,
    prestamos_vencidos
)
from modelos.sede import Sede
from modelos.socio import Socio
from modelos.libro import Libro
from modelos.ejemplar import Ejemplar

ARCHIVO_TEST = "test_reportes.db"


def setup_function():
    if os.path.exists(ARCHIVO_TEST):
        os.remove(ARCHIVO_TEST)
    crear_tablas(ARCHIVO_TEST)


def teardown_function():
    if os.path.exists(ARCHIVO_TEST):
        os.remove(ARCHIVO_TEST)


def crear_base():
    centro = Sede("Centro", "Colon 100", "111", "centro@mail.com", "8 a 20")
    norte = Sede("Norte", "Rivadavia 200", "222", "norte@mail.com", "8 a 20")
    agregar_sede(centro, ARCHIVO_TEST)
    agregar_sede(norte, ARCHIVO_TEST)

    socio = Socio("40111222", "Ana", "Perez", "111", "ana@mail.com")
    agregar_socio(socio, ARCHIVO_TEST)

    libro1 = Libro("9789500000001", "Uno", "Autor A", "Editorial", 2020)
    libro2 = Libro("9789500000002", "Dos", "Autor B", "Editorial", 2021)
    agregar_libro(libro1, ARCHIVO_TEST)
    agregar_libro(libro2, ARCHIVO_TEST)

    ejemplar1 = Ejemplar("EJ-001", libro1, centro)
    ejemplar2 = Ejemplar("EJ-002", libro2, centro)
    agregar_ejemplar(ejemplar1, ARCHIVO_TEST)
    agregar_ejemplar(ejemplar2, ARCHIVO_TEST)
    return centro, norte, socio, ejemplar1, ejemplar2


def test_reporte_prestamos_activos_y_material_en_transito():
    centro, norte, socio, ejemplar1, ejemplar2 = crear_base()
    registrar_prestamo_local(socio.id, ejemplar1.id, centro.id,
                             nombre_archivo=ARCHIVO_TEST)
    _, id_prestamo = solicitar_prestamo_interbibliotecario(
        socio.id, ejemplar2.id, norte.id, ARCHIVO_TEST)
    _, id_remito = crear_remito(id_prestamo, "R-001", ARCHIVO_TEST)
    cambiar_estado_remito(id_remito, "DESPACHADO", nombre_archivo=ARCHIVO_TEST)

    reporte = prestamos_activos_y_material_en_transito(ARCHIVO_TEST)
    assert len(reporte["prestamos_activos"]) == 1
    assert len(reporte["material_en_transito"]) == 1


def test_reporte_libros_mas_solicitados_interbibliotecarios():
    _, norte, socio, _, ejemplar2 = crear_base()
    solicitar_prestamo_interbibliotecario(
        socio.id, ejemplar2.id, norte.id, ARCHIVO_TEST)

    reporte = libros_mas_solicitados_interbibliotecarios(ARCHIVO_TEST)
    assert reporte[0][1] == "Dos"
    assert reporte[0][2] == 1


def test_reporte_disponibilidad_catalogo_por_sede():
    crear_base()
    reporte = disponibilidad_catalogo_por_sede(ARCHIVO_TEST)
    assert len(reporte) == 2
    assert reporte[0][0] == "Centro"


def test_reporte_movimientos_y_promedio_transito():
    _, norte, socio, _, ejemplar2 = crear_base()
    _, id_prestamo = solicitar_prestamo_interbibliotecario(
        socio.id, ejemplar2.id, norte.id, ARCHIVO_TEST)
    _, id_remito = crear_remito(id_prestamo, "R-001", ARCHIVO_TEST)
    cambiar_estado_remito(id_remito, "DESPACHADO", nombre_archivo=ARCHIVO_TEST)
    cambiar_estado_remito(id_remito, "EN_TRANSITO", nombre_archivo=ARCHIVO_TEST)
    cambiar_estado_remito(id_remito, "RECIBIDO", nombre_archivo=ARCHIVO_TEST)

    reporte = movimientos_y_tiempo_promedio_transito(ARCHIVO_TEST)
    assert reporte["movimientos"][0][0] == "Centro"
    assert reporte["movimientos"][0][1] == "Norte"
    assert reporte["movimientos"][0][2] == 1
    assert reporte["horas_promedio_transito"] >= 0


def test_reporte_prestamos_vencidos():
    centro, _, socio, ejemplar1, _ = crear_base()
    ok, id_prestamo = registrar_prestamo_local(
        socio.id, ejemplar1.id, centro.id, nombre_archivo=ARCHIVO_TEST)
    assert ok

    conexion = conectar(ARCHIVO_TEST)
    conexion.execute("""
        UPDATE prestamos
        SET fecha_vencimiento = '2020-01-01'
        WHERE id = ?
    """, (id_prestamo,))
    conexion.commit()
    conexion.close()

    reporte = prestamos_vencidos(ARCHIVO_TEST)
    assert len(reporte) == 1
    assert reporte[0][0] == id_prestamo
    assert reporte[0][3] == "Uno"
