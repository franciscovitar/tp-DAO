import os

from datos.base_datos import crear_tablas
from datos.sedes import agregar_sede, buscar_sede, modificar_sede, cambiar_estado_sede
from datos.socios import agregar_socio, buscar_socio_por_dni, cambiar_habilitacion_socio
from datos.libros import agregar_libro, buscar_libro_por_isbn
from datos.ejemplares import agregar_ejemplar, buscar_ejemplar_por_codigo, listar_ejemplares
from modelos.sede import Sede
from modelos.socio import Socio
from modelos.libro import Libro
from modelos.ejemplar import Ejemplar

ARCHIVO_TEST = "test_biblioteca.db"


def setup_function():
    if os.path.exists(ARCHIVO_TEST):
        os.remove(ARCHIVO_TEST)
    crear_tablas(ARCHIVO_TEST)


def teardown_function():
    if os.path.exists(ARCHIVO_TEST):
        os.remove(ARCHIVO_TEST)


def test_alta_y_modificacion_de_sede():
    sede = Sede("Centro", "Colon 100", "111", "centro@mail.com", "8 a 20")
    agregar_sede(sede, ARCHIVO_TEST)

    encontrada = buscar_sede(sede.id, ARCHIVO_TEST)
    assert encontrada[1] == "Centro"
    assert encontrada[6] == 1

    sede.telefono = "222"
    assert modificar_sede(sede, ARCHIVO_TEST)
    assert buscar_sede(sede.id, ARCHIVO_TEST)[3] == "222"

    assert cambiar_estado_sede(sede.id, False, ARCHIVO_TEST)
    assert buscar_sede(sede.id, ARCHIVO_TEST)[6] == 0


def test_no_agrega_dos_socios_con_el_mismo_dni():
    socio1 = Socio("40111222", "Ana", "Perez", "111", "ana@mail.com")
    socio2 = Socio("40111222", "Juan", "Lopez", "222", "juan@mail.com")

    assert agregar_socio(socio1, ARCHIVO_TEST)
    assert not agregar_socio(socio2, ARCHIVO_TEST)
    assert buscar_socio_por_dni("40111222", ARCHIVO_TEST)[2] == "Ana"

    assert cambiar_habilitacion_socio(socio1.id, False, ARCHIVO_TEST)
    assert buscar_socio_por_dni("40111222", ARCHIVO_TEST)[6] == 0


def test_no_agrega_dos_libros_con_el_mismo_isbn():
    libro1 = Libro("9789500000001", "Uno", "Autor A", "Editorial", 2020)
    libro2 = Libro("9789500000001", "Dos", "Autor B", "Editorial", 2021)

    assert agregar_libro(libro1, ARCHIVO_TEST)
    assert not agregar_libro(libro2, ARCHIVO_TEST)
    assert buscar_libro_por_isbn("9789500000001", ARCHIVO_TEST)[2] == "Uno"


def test_alta_de_ejemplar_y_control_de_codigo_duplicado():
    sede = Sede("Centro", "Colon 100", "111", "centro@mail.com", "8 a 20")
    agregar_sede(sede, ARCHIVO_TEST)

    libro = Libro("9789500000001", "Uno", "Autor A", "Editorial", 2020)
    agregar_libro(libro, ARCHIVO_TEST)

    ejemplar1 = Ejemplar("EJ-001", libro, sede)
    ejemplar2 = Ejemplar("EJ-001", libro, sede)

    assert agregar_ejemplar(ejemplar1, ARCHIVO_TEST)
    assert not agregar_ejemplar(ejemplar2, ARCHIVO_TEST)

    guardado = buscar_ejemplar_por_codigo("EJ-001", ARCHIVO_TEST)
    assert guardado[5] == "DISPONIBLE"
    assert guardado[6] == "BUENO"

    listado = listar_ejemplares(ARCHIVO_TEST)
    assert len(listado) == 1
    assert listado[0][2] == "Uno"
