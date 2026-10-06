import os

from datos.base_datos import crear_tablas
from datos.sedes import agregar_sede
from datos.socios import agregar_socio
from datos.libros import agregar_libro
from datos.ejemplares import agregar_ejemplar, buscar_ejemplar_por_codigo
from datos.prestamos import (
    solicitar_prestamo_interbibliotecario,
    activar_prestamo_interbibliotecario,
    buscar_prestamo
)
from datos.remitos import (
    crear_remito,
    cambiar_estado_remito,
    buscar_remito,
    listar_historial_remito
)
from modelos.sede import Sede
from modelos.socio import Socio
from modelos.libro import Libro
from modelos.ejemplar import Ejemplar

ARCHIVO_TEST = "test_remitos.db"


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


def test_flujo_interbibliotecario_hasta_activar_prestamo():
    origen, destino, socio, ejemplar = crear_datos()

    ok, id_prestamo = solicitar_prestamo_interbibliotecario(
        socio.id, ejemplar.id, destino.id, ARCHIVO_TEST)
    assert ok
    assert buscar_prestamo(id_prestamo, ARCHIVO_TEST)[9] == "SOLICITADO"
    assert buscar_ejemplar_por_codigo("EJ-001", ARCHIVO_TEST)[5] == "RESERVADO"

    ok, id_remito = crear_remito(id_prestamo, "R-001", ARCHIVO_TEST)
    assert ok
    assert buscar_remito(id_remito, ARCHIVO_TEST)[8] == "PREPARADO"

    assert cambiar_estado_remito(
        id_remito, "DESPACHADO", nombre_archivo=ARCHIVO_TEST)[0]
    assert buscar_ejemplar_por_codigo("EJ-001", ARCHIVO_TEST)[5] == "EN_TRANSITO"

    assert cambiar_estado_remito(
        id_remito, "EN_TRANSITO", nombre_archivo=ARCHIVO_TEST)[0]
    assert cambiar_estado_remito(
        id_remito, "RECIBIDO", nombre_archivo=ARCHIVO_TEST)[0]

    ejemplar_guardado = buscar_ejemplar_por_codigo("EJ-001", ARCHIVO_TEST)
    assert ejemplar_guardado[4] == destino.id
    assert ejemplar_guardado[5] == "RESERVADO"

    estados = [fila[0] for fila in listar_historial_remito(
        id_remito, ARCHIVO_TEST)]
    assert estados == ["PREPARADO", "DESPACHADO", "EN_TRANSITO", "RECIBIDO"]

    ok, _ = activar_prestamo_interbibliotecario(
        id_prestamo, nombre_archivo=ARCHIVO_TEST)
    assert ok
    assert buscar_prestamo(id_prestamo, ARCHIVO_TEST)[9] == "ACTIVO"
    assert buscar_ejemplar_por_codigo("EJ-001", ARCHIVO_TEST)[5] == "PRESTADO"


def test_no_permite_saltar_estados_del_remito():
    _, destino, socio, ejemplar = crear_datos()
    _, id_prestamo = solicitar_prestamo_interbibliotecario(
        socio.id, ejemplar.id, destino.id, ARCHIVO_TEST)
    _, id_remito = crear_remito(id_prestamo, "R-001", ARCHIVO_TEST)

    ok, mensaje = cambiar_estado_remito(
        id_remito, "RECIBIDO", nombre_archivo=ARCHIVO_TEST)

    assert not ok
    assert mensaje == "Cambio de estado no permitido"
    estados = [fila[0] for fila in listar_historial_remito(
        id_remito, ARCHIVO_TEST)]
    assert estados == ["PREPARADO"]
