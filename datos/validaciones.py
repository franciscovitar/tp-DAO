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
# Parte local y dominio sin puntos al principio, al final ni consecutivos
_EMAIL = re.compile(
    r"[A-Za-z0-9_%+-]+(\.[A-Za-z0-9_%+-]+)*@[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}"
)
_TELEFONO = re.compile(r"\+?[0-9 ()-]+")
_CODIGO = re.compile(r"[A-Za-z0-9-]+")

# Horario de atención: "9 a 18", "09:00-18:00", "Lun a Vie 9:00 a 18:00",
# varios tramos separados por coma, punto y coma o "y".
_DIA = r"(?:lun|mar|mi[eé]|jue|vie|s[aá]b|dom)[a-záéíóú]*\.?"
_DIAS = rf"{_DIA}(?:\s*(?:a|al|-|y|,)\s*{_DIA})*"
_HORA = r"(\d{1,2})(?::(\d{2}))?\s*(?:hs|hrs|h)?\.?"
_TRAMO = rf"(?:{_DIAS}\s*:?\s*)?{_HORA}\s*(?:a|-|–|hasta)\s*{_HORA}"
_TRAMO_RE = re.compile(_TRAMO, re.IGNORECASE)
_HORARIO_RE = re.compile(rf"{_TRAMO}(?:\s*(?:,|;|y)\s*{_TRAMO})*", re.IGNORECASE)


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


_LETRAS = "A-Za-zÁÉÍÓÚÜÑáéíóúüñ"
_NOMBRE_SEDE = re.compile(rf"[{_LETRAS}0-9 .'-]+")
_DIRECCION = re.compile(rf"[{_LETRAS}0-9 .,°º#/-]+")
_AUTOR = re.compile(rf"[{_LETRAS} .,'&-]+")
_TITULO = re.compile(rf"[{_LETRAS}0-9 .,:;¡!¿?'\"()&/+#-]+")


def validar_nombre_sede(texto):
    ok, valor = validar_texto(texto, "nombre", LARGO_NOMBRE)
    if not ok:
        return ok, valor
    if not _NOMBRE_SEDE.fullmatch(valor) or sum(c.isalpha() for c in valor) < 2:
        return False, "El nombre de la sede debe tener letras (se permiten números, puntos y guiones)."
    return True, " ".join(valor.split())


def validar_direccion(texto):
    ok, valor = validar_texto(texto, "dirección", LARGO_DIRECCION)
    if not ok:
        return ok, valor
    tiene_calle = re.search(rf"[{_LETRAS}]{{3,}}", valor) is not None
    tiene_altura = any(c.isdigit() for c in valor)
    if not _DIRECCION.fullmatch(valor) or not tiene_calle or not tiene_altura:
        return False, "La dirección debe tener calle y altura (ejemplo: Av. Colón 1200)."
    return True, " ".join(valor.split())


def validar_titulo(texto, campo, largo_maximo, obligatorio=True, requiere_letras=False):
    ok, valor = validar_texto(texto, campo, largo_maximo, obligatorio)
    if not ok or valor == "":
        return ok, valor
    letras = sum(c.isalpha() for c in valor)
    digitos = sum(c in "0123456789" for c in valor)
    # Debe tener alguna letra; un título puede ser sólo un número de 3 o 4 cifras (p. ej. «1984»)
    solo_numero_valido = (not requiere_letras and 3 <= digitos <= 4
                          and valor.strip("0") != "" and valor.isdigit())
    if not _TITULO.fullmatch(valor) or (letras == 0 and not solo_numero_valido):
        if requiere_letras:
            return False, f"El campo {campo} debe tener letras."
        return False, (f"El campo {campo} debe tener letras (o ser un número de 3 o 4 cifras, como «1984») "
                       "y sólo signos de puntuación comunes.")
    return True, " ".join(valor.split())


def validar_autor(texto):
    ok, valor = validar_texto(texto, "autor", LARGO_AUTOR)
    if not ok:
        return ok, valor
    if not _AUTOR.fullmatch(valor) or sum(c.isalpha() for c in valor) < 2:
        return False, "El autor sólo puede contener letras (se permiten puntos, comas y guiones)."
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
    if not _TELEFONO.fullmatch(valor) or not 8 <= digitos <= 15:
        return False, "El teléfono debe tener entre 8 y 15 dígitos (se permiten +, espacios, guiones y paréntesis)."
    if len({c for c in valor if c.isdigit()}) == 1:
        return False, "El teléfono no puede tener todos los dígitos iguales."
    return True, valor


def validar_horario(texto):
    ok, valor = validar_texto(texto, "horario", LARGO_HORARIO, obligatorio=False)
    if not ok or valor == "":
        return ok, valor
    error = (False, "El horario no es válido. Ejemplos: «9 a 18», «09:00-18:00», "
                    "«Lun a Vie 9:00 a 18:00».")
    if not _HORARIO_RE.fullmatch(valor):
        return error
    for tramo in _TRAMO_RE.finditer(valor):
        h1, m1, h2, m2 = (int(x) if x else 0 for x in tramo.groups())
        if h1 > 24 or h2 > 24 or m1 > 59 or m2 > 59:
            return error
        if h1 * 60 + m1 >= h2 * 60 + m2:
            return False, "En el horario, la hora de apertura debe ser anterior a la de cierre."
    return True, " ".join(valor.split())


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
    if not _CODIGO.fullmatch(valor) or valor.startswith("-") or valor.endswith("-"):
        return False, f"El {campo} sólo puede contener letras, números y guiones (sin guion al principio ni al final)."
    if len(valor) < 2:
        return False, f"El {campo} debe tener al menos 2 caracteres."
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
        ("nombre", validar_nombre_sede(nombre)),
        ("direccion", validar_direccion(direccion)),
        ("telefono", validar_telefono(telefono)),
        ("email", validar_email(email)),
        ("horario", validar_horario(horario)),
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
        ("titulo", validar_titulo(titulo, "título", LARGO_TITULO)),
        ("autor", validar_autor(autor)),
        ("editorial", validar_titulo(editorial, "editorial", LARGO_EDITORIAL, obligatorio=False,
                                     requiere_letras=True)),
        ("anio", validar_anio(anio)),
    ])
