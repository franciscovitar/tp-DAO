import os

from datos.base_datos import crear_tablas
from datos.sedes import agregar_sede, buscar_sede, modificar_sede, cambiar_estado_sede
from datos.socios import agregar_socio, buscar_socio_por_dni, cambiar_habilitacion_socio
from datos.libros import agregar_libro, buscar_libro_por_isbn
from datos.ejemplares import agregar_ejemplar, buscar_ejemplar_por_codigo, listar_ejemplares, cambiar_estado_ejemplar
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


def test_ejemplar_disponible_puede_activarse_y_desactivarse():
    sede = Sede("Centro", "Colon 100", "111", "centro@mail.com", "8 a 20")
    agregar_sede(sede, ARCHIVO_TEST)

    libro = Libro("9789500000001", "Uno", "Autor A", "Editorial", 2020)
    agregar_libro(libro, ARCHIVO_TEST)

    ejemplar = Ejemplar("EJ-001", libro, sede)
    agregar_ejemplar(ejemplar, ARCHIVO_TEST)

    assert cambiar_estado_ejemplar(ejemplar.id, "BAJA", ARCHIVO_TEST)
    assert buscar_ejemplar_por_codigo("EJ-001", ARCHIVO_TEST)[5] == "BAJA"

    assert cambiar_estado_ejemplar(ejemplar.id, "DISPONIBLE", ARCHIVO_TEST)
    assert buscar_ejemplar_por_codigo("EJ-001", ARCHIVO_TEST)[5] == "DISPONIBLE"


def test_no_desactiva_un_ejemplar_prestado():
    sede, socio, ejemplar = crear_datos_para_prestamo()
    from datos.prestamos import registrar_prestamo_local

    ok, _ = registrar_prestamo_local(
        socio.id, ejemplar.id, sede.id, nombre_archivo=ARCHIVO_TEST)
    assert ok

    assert not cambiar_estado_ejemplar(ejemplar.id, "BAJA", ARCHIVO_TEST)
    assert buscar_ejemplar_por_codigo("EJ-001", ARCHIVO_TEST)[5] == "PRESTADO"


def crear_datos_para_prestamo():
    sede = Sede("Centro", "Colon 100", "111", "centro@mail.com", "8 a 20")
    agregar_sede(sede, ARCHIVO_TEST)

    socio = Socio("40111222", "Ana", "Perez", "111", "ana@mail.com")
    agregar_socio(socio, ARCHIVO_TEST)

    libro = Libro("9789500000001", "Uno", "Autor A", "Editorial", 2020)
    agregar_libro(libro, ARCHIVO_TEST)

    ejemplar = Ejemplar("EJ-001", libro, sede)
    agregar_ejemplar(ejemplar, ARCHIVO_TEST)
    return sede, socio, ejemplar


def test_registrar_prestamo_local_cambia_estado_del_ejemplar():
    from datos.prestamos import registrar_prestamo_local, buscar_prestamo

    sede, socio, ejemplar = crear_datos_para_prestamo()
    ok, id_prestamo = registrar_prestamo_local(socio.id, ejemplar.id, sede.id,
                                                nombre_archivo=ARCHIVO_TEST)

    assert ok
    assert buscar_prestamo(id_prestamo, ARCHIVO_TEST)[9] == "ACTIVO"
    assert buscar_ejemplar_por_codigo("EJ-001", ARCHIVO_TEST)[5] == "PRESTADO"


def test_no_presta_a_socio_inhabilitado():
    from datos.prestamos import registrar_prestamo_local

    sede, socio, ejemplar = crear_datos_para_prestamo()
    cambiar_habilitacion_socio(socio.id, False, ARCHIVO_TEST)

    ok, mensaje = registrar_prestamo_local(socio.id, ejemplar.id, sede.id,
                                            nombre_archivo=ARCHIVO_TEST)

    assert not ok
    assert mensaje == "El socio está inhabilitado"
    assert buscar_ejemplar_por_codigo("EJ-001", ARCHIVO_TEST)[5] == "DISPONIBLE"


def test_no_presta_desde_una_sede_dada_de_baja():
    from datos.prestamos import registrar_prestamo_local

    sede, socio, ejemplar = crear_datos_para_prestamo()
    cambiar_estado_sede(sede.id, False, ARCHIVO_TEST)

    ok, mensaje = registrar_prestamo_local(socio.id, ejemplar.id, sede.id,
                                            nombre_archivo=ARCHIVO_TEST)

    assert not ok
    assert mensaje == "La sede está dada de baja"


def test_no_presta_un_ejemplar_de_otra_sede():
    from datos.prestamos import registrar_prestamo_local

    sede, socio, ejemplar = crear_datos_para_prestamo()
    otra = Sede("Norte", "Rivadavia 200", "222", "norte@mail.com", "8 a 20")
    agregar_sede(otra, ARCHIVO_TEST)

    ok, mensaje = registrar_prestamo_local(socio.id, ejemplar.id, otra.id,
                                            nombre_archivo=ARCHIVO_TEST)

    assert not ok
    assert mensaje == "El ejemplar no pertenece a la sede de origen"


def test_devolucion_cierra_prestamo_y_libera_ejemplar():
    from datos.prestamos import registrar_prestamo_local, registrar_devolucion, buscar_prestamo

    sede, socio, ejemplar = crear_datos_para_prestamo()
    ok, id_prestamo = registrar_prestamo_local(socio.id, ejemplar.id, sede.id,
                                                nombre_archivo=ARCHIVO_TEST)
    assert ok

    ok, _ = registrar_devolucion(id_prestamo, "DANADO", ARCHIVO_TEST)

    assert ok
    assert buscar_prestamo(id_prestamo, ARCHIVO_TEST)[9] == "DEVUELTO"
    guardado = buscar_ejemplar_por_codigo("EJ-001", ARCHIVO_TEST)
    assert guardado[5] == "DISPONIBLE"
    assert guardado[6] == "DANADO"


def test_reserva_marca_el_ejemplar_como_reservado():
    from datos.reservas import registrar_reserva, buscar_reserva

    sede, socio, ejemplar = crear_datos_para_prestamo()
    ok, id_reserva = registrar_reserva(socio.id, ejemplar.id, sede.id,
                                       ARCHIVO_TEST)

    assert ok
    assert buscar_reserva(id_reserva, ARCHIVO_TEST)[5] == "ACTIVA"
    assert buscar_ejemplar_por_codigo("EJ-001", ARCHIVO_TEST)[5] == "RESERVADO"


def test_otro_socio_no_puede_prestar_un_ejemplar_reservado():
    from datos.reservas import registrar_reserva
    from datos.prestamos import registrar_prestamo_local

    sede, socio, ejemplar = crear_datos_para_prestamo()
    otro = Socio("40999888", "Juan", "Lopez", "222", "juan@mail.com")
    agregar_socio(otro, ARCHIVO_TEST)
    registrar_reserva(socio.id, ejemplar.id, sede.id, ARCHIVO_TEST)

    ok, mensaje = registrar_prestamo_local(otro.id, ejemplar.id, sede.id,
                                            nombre_archivo=ARCHIVO_TEST)

    assert not ok
    assert mensaje == "El ejemplar está reservado para otro socio"


def test_socio_que_reservo_puede_concretar_el_prestamo():
    from datos.reservas import registrar_reserva, buscar_reserva
    from datos.prestamos import registrar_prestamo_local

    sede, socio, ejemplar = crear_datos_para_prestamo()
    _, id_reserva = registrar_reserva(socio.id, ejemplar.id, sede.id,
                                      ARCHIVO_TEST)

    ok, _ = registrar_prestamo_local(socio.id, ejemplar.id, sede.id,
                                      nombre_archivo=ARCHIVO_TEST)

    assert ok
    assert buscar_reserva(id_reserva, ARCHIVO_TEST)[5] == "CUMPLIDA"
    assert buscar_ejemplar_por_codigo("EJ-001", ARCHIVO_TEST)[5] == "PRESTADO"


def test_cancelar_reserva_libera_el_ejemplar():
    from datos.reservas import registrar_reserva, cancelar_reserva, buscar_reserva

    sede, socio, ejemplar = crear_datos_para_prestamo()
    _, id_reserva = registrar_reserva(socio.id, ejemplar.id, sede.id,
                                      ARCHIVO_TEST)

    ok, _ = cancelar_reserva(id_reserva, ARCHIVO_TEST)

    assert ok
    assert buscar_reserva(id_reserva, ARCHIVO_TEST)[5] == "CANCELADA"
    assert buscar_ejemplar_por_codigo("EJ-001", ARCHIVO_TEST)[5] == "DISPONIBLE"
