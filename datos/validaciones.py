"""Validaciones de datos de entrada.

Cada función recibe el texto ingresado y devuelve una tupla (ok, valor_o_mensaje):
si ok es True, el segundo elemento es el valor limpio/normalizado; si es False,
es el mensaje de error para mostrar al usuario.
"""

import re
from datetime import date

MIN_DIAS_PRESTAMO = 1
MAX_DIAS_PRESTAMO = 60
ANIO_MINIMO_LIBRO = 1450  # imprenta de Gutenberg

LARGO_NOMBRE = 80
LARGO_DIRECCION = 120
LARGO_HORARIO = 80
LARGO_EMAIL = 100
LARGO_TITULO = 200
LARGO_AUTOR = 120
LARGO_EDITORIAL = 100
LARGO_CODIGO = 30

_SOLO_DIGITOS = re.compile(r"[0-9]+")
_NOMBRE_PERSONA = re.compile(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ' .-]+")
_EMAIL = re.compile(r"[^@\s]+@[^@\s]+\.[A-Za-z]{2,}")
_TELEFONO = re.compile(r"\+?[0-9 ()-]+")
_CODIGO = re.compile(r"[A-Za-z0-9-]+")


def validar_texto(valor, campo, largo_maximo, obligatorio=True):
    valor = (valor or "").strip()
    if not valor:
        if obligatorio:
            return False, f"El campo {campo} es obligatorio."
        return True, ""
    if len(valor) > largo_maximo:
        return False, f"El campo {campo} admite como máximo {largo_maximo} caracteres."
    return True, valor


def validar_entero(texto, campo, minimo, maximo):
    texto = (texto or "").strip()
    # fullmatch con [0-9] evita aceptar caracteres como "²" que isdigit() deja pasar
    if not _SOLO_DIGITOS.fullmatch(texto):
        return False, f"{campo} debe ser un número entero."
    if len(texto) > 9:
        return False, f"{campo} debe estar entre {minimo} y {maximo}."
    numero = int(texto)
    if numero < minimo or numero > maximo:
        return False, f"{campo} debe estar entre {minimo} y {maximo}."
    return True, numero


def validar_dias_prestamo(texto):
    if isinstance(texto, int):
        texto = str(texto)
    return validar_entero(texto, "La cantidad de días", MIN_DIAS_PRESTAMO, MAX_DIAS_PRESTAMO)


def validar_dni(texto):
    dni = (texto or "").strip().replace(".", "").replace(" ", "")
    if not _SOLO_DIGITOS.fullmatch(dni):
        return False, "El DNI debe contener solamente números."
    dni = dni.lstrip("0")
    if not 7 <= len(dni) <= 8:
        return False, "El DNI debe tener 7 u 8 dígitos."
    return True, dni


def validar_nombre_persona(texto, campo):
    ok, valor = validar_texto(texto, campo, LARGO_NOMBRE)
    if not ok:
        return ok, valor
    if not _NOMBRE_PERSONA.fullmatch(valor) or not any(c.isalpha() for c in valor):
        return False, f"El campo {campo} sólo puede contener letras."
    return True, " ".join(valor.split())


def validar_email(texto):
    ok, valor = validar_texto(texto, "email", LARGO_EMAIL, obligatorio=False)
    if not ok or valor == "":
        return ok, valor
    if not _EMAIL.fullmatch(valor):
        return False, "El email no tiene un formato válido (ejemplo: nombre@dominio.com)."
    return True, valor.lower()


def validar_telefono(texto):
    valor = (texto or "").strip()
    if valor == "":
        return True, ""
    digitos = sum(c.isdigit() for c in valor)
    if not _TELEFONO.fullmatch(valor) or not 6 <= digitos <= 15:
        return False, "El teléfono debe tener entre 6 y 15 dígitos (se permiten +, espacios, guiones y paréntesis)."
    return True, valor


def validar_isbn(texto):
    isbn = (texto or "").strip().replace("-", "").replace(" ", "").upper()
    if len(isbn) == 13 and _SOLO_DIGITOS.fullmatch(isbn):
        return True, isbn
    if len(isbn) == 10 and _SOLO_DIGITOS.fullmatch(isbn[:9]) and (isbn[9].isdigit() or isbn[9] == "X"):
        return True, isbn
    return False, "El ISBN debe tener 10 o 13 dígitos (se permiten guiones)."


def validar_anio(texto):
    texto = (texto or "").strip()
    if texto == "":
        return True, None
    return validar_entero(texto, "El año", ANIO_MINIMO_LIBRO, date.today().year)


def validar_codigo(texto, campo):
    ok, valor = validar_texto(texto, campo, LARGO_CODIGO)
    if not ok:
        return ok, valor
    if not _CODIGO.fullmatch(valor):
        return False, f"El {campo} sólo puede contener letras, números y guiones."
    return True, valor.upper()


def _aplicar(validaciones):
    resultado = {}
    for clave, (ok, valor) in validaciones:
        if not ok:
            return False, valor
        resultado[clave] = valor
    return True, resultado


def validar_datos_sede(nombre, direccion, telefono, email, horario):
    return _aplicar([
        ("nombre", validar_texto(nombre, "nombre", LARGO_NOMBRE)),
        ("direccion", validar_texto(direccion, "dirección", LARGO_DIRECCION)),
        ("telefono", validar_telefono(telefono)),
        ("email", validar_email(email)),
        ("horario", validar_texto(horario, "horario", LARGO_HORARIO, obligatorio=False)),
    ])


def validar_datos_socio(dni, nombre, apellido, telefono, email):
    return _aplicar([
        ("dni", validar_dni(dni)),
        ("nombre", validar_nombre_persona(nombre, "nombre")),
        ("apellido", validar_nombre_persona(apellido, "apellido")),
        ("telefono", validar_telefono(telefono)),
        ("email", validar_email(email)),
    ])


def validar_datos_libro(isbn, titulo, autor, editorial, anio):
    return _aplicar([
        ("isbn", validar_isbn(isbn)),
        ("titulo", validar_texto(titulo, "título", LARGO_TITULO)),
        ("autor", validar_texto(autor, "autor", LARGO_AUTOR)),
        ("editorial", validar_texto(editorial, "editorial", LARGO_EDITORIAL, obligatorio=False)),
        ("anio", validar_anio(anio)),
    ])
