import os

import pytest

from datos.base_datos import crear_tablas, DatabaseSingleton
from datos.prestamos import registrar_prestamo_local
from datos.remitos import crear_remito
from datos.sedes import agregar_sede, modificar_sede
from datos.validaciones import (
    validar_anio,
    validar_datos_libro,
    validar_datos_sede,
    validar_datos_socio,
    validar_dias_prestamo,
    validar_dni,
    validar_email,
    validar_isbn,
    validar_telefono,
)
from modelos.sede import Sede

ARCHIVO_TEST = "test_validaciones.db"


@pytest.fixture(autouse=True)
def base_limpia():
    DatabaseSingleton().close_connection()
    if os.path.exists(ARCHIVO_TEST):
        os.remove(ARCHIVO_TEST)
    crear_tablas(ARCHIVO_TEST)
    yield
    DatabaseSingleton().close_connection()
    if os.path.exists(ARCHIVO_TEST):
        os.remove(ARCHIVO_TEST)


@pytest.mark.parametrize("valor", ["0", "-5", "61", "99999999999", "abc", "", " ", "7.5", "²", "1e3"])
def test_dias_invalidos(valor):
    ok, _ = validar_dias_prestamo(valor)
    assert not ok


@pytest.mark.parametrize("valor, esperado", [("1", 1), (" 14 ", 14), ("60", 60)])
def test_dias_validos(valor, esperado):
    assert validar_dias_prestamo(valor) == (True, esperado)


def test_prestamo_con_dias_enormes_no_rompe():
    # Antes: date.today() + timedelta(days=99999999) lanzaba OverflowError
    ok, mensaje = registrar_prestamo_local(1, 1, 1, 99999999, ARCHIVO_TEST)
    assert not ok
    assert "entre 1 y 60" in mensaje


@pytest.mark.parametrize("valor", ["", "123", "123456789", "12a45678", "-1234567", "0000000"])
def test_dni_invalido(valor):
    assert not validar_dni(valor)[0]


def test_dni_normaliza_puntos_y_ceros():
    assert validar_dni("40.111.222") == (True, "40111222")
    assert validar_dni("040111222") == (True, "40111222")


@pytest.mark.parametrize("valor", ["123", "978-950-000", "97895000000011", "ABCDEFGHIJ", "123456789Y"])
def test_isbn_invalido(valor):
    assert not validar_isbn(valor)[0]


def test_isbn_normaliza_guiones():
    assert validar_isbn("978-950-000-000-1") == (True, "9789500000001")
    assert validar_isbn("0-306-40615-x") == (True, "030640615X")


@pytest.mark.parametrize("valor", ["0", "-1", "1200", "3000", "99999999999999", "dos mil"])
def test_anio_invalido(valor):
    assert not validar_anio(valor)[0]


def test_anio_vacio_es_opcional():
    assert validar_anio("") == (True, None)


@pytest.mark.parametrize("valor", ["sin-arroba", "a@b", "a@@b.com", "a b@c.com"])
def test_email_invalido(valor):
    assert not validar_email(valor)[0]


@pytest.mark.parametrize("valor", ["12", "telefono", "1" * 30])
def test_telefono_invalido(valor):
    assert not validar_telefono(valor)[0]


def test_textos_demasiado_largos():
    assert not validar_datos_sede("A" * 500, "Calle 1", "", "", "")[0]
    assert not validar_datos_libro("9789500000001", "T" * 1000, "Autor", "", "")[0]


def test_nombre_de_socio_con_numeros_o_solo_espacios():
    assert not validar_datos_socio("40111222", "Ana123", "Perez", "", "")[0]
    assert not validar_datos_socio("40111222", "   ", "Perez", "", "")[0]
    ok, datos = validar_datos_socio("40111222", "  María  José ", "O'Neil", "", "")
    assert ok and datos["nombre"] == "María José"


def test_no_duplica_sede_con_mismo_nombre_y_direccion():
    assert agregar_sede(Sede("Centro", "Colon 100", "", "", ""), ARCHIVO_TEST)
    assert agregar_sede(Sede("CENTRO", "colon 100", "", "", ""), ARCHIVO_TEST) is None
    # Mismo nombre pero otra dirección se permite (sedes de distintas ciudades)
    assert agregar_sede(Sede("Centro", "Rivadavia 200", "", "", ""), ARCHIVO_TEST)


def test_no_modifica_sede_para_duplicar_otra():
    agregar_sede(Sede("Centro", "Colon 100", "", "", ""), ARCHIVO_TEST)
    otra = Sede("Norte", "Mitre 5", "", "", "")
    agregar_sede(otra, ARCHIVO_TEST)
    otra.nombre, otra.direccion = "Centro", "Colon 100"
    assert not modificar_sede(otra, ARCHIVO_TEST)


def test_numero_de_remito_con_caracteres_invalidos():
    ok, mensaje = crear_remito(1, "R 001; DROP TABLE", ARCHIVO_TEST)
    assert not ok
    assert "letras, números y guiones" in mensaje
