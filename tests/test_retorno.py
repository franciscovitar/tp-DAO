import os

from datos.base_datos import crear_tablas
from datos.sedes import agregar_sede
from datos.socios import agregar_socio
from datos.libros import agregar_libro
from datos.ejemplares import agregar_ejemplar, buscar_ejemplar_por_codigo
from datos.prestamos import (
    solicitar_prestamo_interbibliotecario,
    activar_prestamo_interbibliotecario,
    registrar_devolucion,
    listar_prestamos_pendientes_retorno
)
from datos.remitos import (
    crear_remito,
    crear_remito_retorno,
    cambiar_estado_remito,
    listar_historial_remito
)
from datos.reportes import disponibilidad_catalogo_por_sede
from modelos.sede import Sede
from modelos.socio import Socio
from modelos.libro import Libro
from modelos.ejemplar import Ejemplar

ARCHIVO_TEST = "test_retorno.db"


def setup_function():
    if os.path.exists(ARCHIVO_TEST):
        os.remove(ARCHIVO_TEST)
    crear_tablas(ARCHIVO_TEST)


def teardown_function():
    if os.path.exists(ARCHIVO_TEST):
        os.remove(ARCHIVO_TEST)


def crear_datos():
    origen = Sede("Centro", "Colon 100", "111", "centro@mail.com", "8 a 20")
    destino = Sede("Norte", "Rivadavia 200", "222", "norte@mail.com", "8 a 20")
    agregar_sede(origen, ARCHIVO_TEST)
    agregar_sede(destino, ARCHIVO_TEST)

    socio = Socio("40111222", "Ana", "Perez", "111", "ana@mail.com")
    agregar_socio(socio, ARCHIVO_TEST)

    libro = Libro("9789500000001", "Uno", "Autor", "Editorial", 2020)
    agregar_libro(libro, ARCHIVO_TEST)

    ejemplar = Ejemplar("EJ-001", libro, origen)
    agregar_ejemplar(ejemplar, ARCHIVO_TEST)
    return origen, destino, socio, ejemplar


def avanzar_hasta_recibido(id_remito):
    for estado in ("DESPACHADO", "EN_TRANSITO", "RECIBIDO"):
        ok, _ = cambiar_estado_remito(
            id_remito, estado, nombre_archivo=ARCHIVO_TEST)
        assert ok


def test_ejemplar_interbibliotecario_vuelve_a_su_sede_de_pertenencia():
    origen, destino, socio, ejemplar = crear_datos()

    ok, id_prestamo = solicitar_prestamo_interbibliotecario(
        socio.id, ejemplar.id, destino.id, ARCHIVO_TEST)
    assert ok

    ok, id_remito_ida = crear_remito(id_prestamo, "IDA-001", ARCHIVO_TEST)
    assert ok
    avanzar_hasta_recibido(id_remito_ida)

    assert activar_prestamo_interbibliotecario(
        id_prestamo, nombre_archivo=ARCHIVO_TEST)[0]
    assert registrar_devolucion(
        id_prestamo, "BUENO", ARCHIVO_TEST)[0]
    assert buscar_ejemplar_por_codigo(
        "EJ-001", ARCHIVO_TEST)[5] == "PENDIENTE_RETORNO"
    assert disponibilidad_catalogo_por_sede(ARCHIVO_TEST) == []

    ok, id_remito_retorno = crear_remito_retorno(
        id_prestamo, "RET-001", ARCHIVO_TEST)
    assert ok
    assert buscar_ejemplar_por_codigo(
        "EJ-001", ARCHIVO_TEST)[5] == "PENDIENTE_RETORNO"

    avanzar_hasta_recibido(id_remito_retorno)

    guardado = buscar_ejemplar_por_codigo("EJ-001", ARCHIVO_TEST)
    assert guardado[4] == origen.id
    assert guardado[5] == "DISPONIBLE"

    estados = [fila[0] for fila in listar_historial_remito(
        id_remito_retorno, ARCHIVO_TEST)]
    assert estados == ["PREPARADO", "DESPACHADO", "EN_TRANSITO", "RECIBIDO"]


def test_no_crea_dos_remitos_de_retorno_para_el_mismo_prestamo():
    origen, destino, socio, ejemplar = crear_datos()

    _, id_prestamo = solicitar_prestamo_interbibliotecario(
        socio.id, ejemplar.id, destino.id, ARCHIVO_TEST)
    _, id_remito_ida = crear_remito(id_prestamo, "IDA-001", ARCHIVO_TEST)
    avanzar_hasta_recibido(id_remito_ida)
    activar_prestamo_interbibliotecario(
        id_prestamo, nombre_archivo=ARCHIVO_TEST)
    registrar_devolucion(id_prestamo, "BUENO", ARCHIVO_TEST)

    assert crear_remito_retorno(
        id_prestamo, "RET-001", ARCHIVO_TEST)[0]

    ok, mensaje = crear_remito_retorno(
        id_prestamo, "RET-002", ARCHIVO_TEST)

    assert not ok
    assert mensaje == "El préstamo ya tiene un remito de retorno"


def test_detecta_retorno_aunque_las_sedes_tengan_el_mismo_nombre():
    origen = Sede("Centro", "Colon 100", "111", "uno@mail.com", "8 a 20")
    destino = Sede("Centro", "Rivadavia 200", "222", "dos@mail.com", "8 a 20")
    agregar_sede(origen, ARCHIVO_TEST)
    agregar_sede(destino, ARCHIVO_TEST)

    socio = Socio("40111222", "Ana", "Perez", "111", "ana@mail.com")
    agregar_socio(socio, ARCHIVO_TEST)

    libro = Libro("9789500000001", "Uno", "Autor", "Editorial", 2020)
    agregar_libro(libro, ARCHIVO_TEST)

    ejemplar = Ejemplar("EJ-001", libro, origen)
    agregar_ejemplar(ejemplar, ARCHIVO_TEST)

    _, id_prestamo = solicitar_prestamo_interbibliotecario(
        socio.id, ejemplar.id, destino.id, ARCHIVO_TEST)
    _, id_remito = crear_remito(id_prestamo, "IDA-001", ARCHIVO_TEST)
    avanzar_hasta_recibido(id_remito)
    activar_prestamo_interbibliotecario(
        id_prestamo, nombre_archivo=ARCHIVO_TEST)
    registrar_devolucion(id_prestamo, "BUENO", ARCHIVO_TEST)

    pendientes = listar_prestamos_pendientes_retorno(ARCHIVO_TEST)

    assert len(pendientes) == 1
    assert pendientes[0][0] == id_prestamo

