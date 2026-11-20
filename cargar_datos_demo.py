"""Carga opcional de datos ficticios para probar y mostrar la biblioteca.

Uso desde la carpeta del proyecto:
    python cargar_datos_demo.py
    python cargar_datos_demo.py --bd otra_biblioteca.db

No borra registros existentes ni vuelve a crear los que ya están cargados.
"""

import argparse

from datos.base_datos import ARCHIVO_BD, DatabaseSingleton, crear_tablas
from datos.ejemplares import agregar_ejemplar, buscar_ejemplar_por_codigo
from datos.libros import agregar_libro, buscar_libro_por_isbn
from datos.prestamos import (
    activar_prestamo_interbibliotecario,
    registrar_devolucion,
    registrar_prestamo_local,
    solicitar_prestamo_interbibliotecario,
)
from datos.remitos import cambiar_estado_remito, crear_remito
from datos.reservas import cancelar_reserva, registrar_reserva
from datos.sedes import agregar_sede, buscar_sede_duplicada
from datos.socios import agregar_socio, buscar_socio_por_dni
from modelos.ejemplar import Ejemplar
from modelos.libro import Libro
from modelos.sede import Sede
from modelos.socio import Socio


SEDES = {
    "Centro": ("Biblioteca Demo Centro", "Av. Colón 1200", "3514441100", "centro@biblioteca.example", "Lun a Vie 9 a 18"),
    "Norte": ("Biblioteca Demo Norte", "Av. Rafael Núñez s/n", "3514442200", "norte@biblioteca.example", "Lun a Vie 9 a 18"),
    "Sur": ("Biblioteca Demo Sur", "Camino de las Sierras", "3514443300", "sur@biblioteca.example", "Lun a Vie 9 a 18"),
}

SOCIOS = {
    "Ana": ("49000001", "Ana", "Pérez", "3515550001", "ana@biblioteca.example"),
    "Juan": ("49000002", "Juan", "Gómez", "3515550002", "juan@biblioteca.example"),
    "Lucía": ("49000003", "Lucía", "Fernández", "3515550003", "lucia@biblioteca.example"),
    "Valentina": ("49000004", "Valentina", "Torres", "3515550004", "valentina@biblioteca.example"),
    "Martín": ("49000005", "Martín", "Rodríguez", "3515550005", "martin@biblioteca.example"),
    "Sofía": ("49000006", "Sofía", "López", "3515550006", "sofia@biblioteca.example"),
    "Mateo": ("49000007", "Mateo", "Díaz", "3515550007", "mateo@biblioteca.example"),
    "Nicolás": ("49000008", "Nicolás", "Herrera", "3515550008", "nicolas@biblioteca.example"),
}

# Los ISBN son identificadores de muestra, no ediciones comerciales reales.
LIBROS = [
    ("9789500000017", "El principito", "Antoine de Saint-Exupéry", "Editorial Demo", 1943),
    ("9789500000024", "Don Quijote de la Mancha", "Miguel de Cervantes", "Editorial Demo", 1605),
    ("9789500000031", "Rayuela", "Julio Cortázar", "Editorial Demo", 1963),
    ("9789500000048", "Ficciones", "Jorge Luis Borges", "Editorial Demo", 1944),
    ("9789500000055", "Cien años de soledad", "Gabriel García Márquez", "Editorial Demo", 1967),
    ("9789500000062", "1984", "George Orwell", "Editorial Demo", 1949),
    ("9789500000079", "La invención de Morel", "Adolfo Bioy Casares", "Editorial Demo", 1940),
    ("9789500000086", "El túnel", "Ernesto Sabato", "Editorial Demo", 1948),
    ("9789500000093", "Programación en Python", "Laura Pérez", "Editorial Demo", 2024),
    ("9789500000109", "Algoritmos para todos", "María González", "Editorial Demo", 2023),
]


def _exigir(resultado, descripcion):
    """Detiene la carga si una regla del negocio rechaza un caso de muestra."""
    correcto, valor = resultado
    if not correcto:
        raise RuntimeError(f"No se pudo {descripcion}: {valor}")
    return valor


def cargar_datos_demo(nombre_archivo=ARCHIVO_BD):
    """Agrega ejemplos faltantes; sólo genera movimientos sobre ejemplares nuevos."""
    crear_tablas(nombre_archivo)
    cantidades = {"sedes": 0, "socios": 0, "libros": 0,
                  "ejemplares": 0, "reservas": 0, "prestamos": 0, "remitos": 0}

    sedes = {}
    for clave, datos in SEDES.items():
        sede = Sede(*datos)
        existente = buscar_sede_duplicada(sede.nombre, sede.direccion, nombre_archivo)
        if existente:
            sede.id = existente[0]
        else:
            sede.id = agregar_sede(sede, nombre_archivo)
            if sede.id is None:
                raise RuntimeError(f"No se pudo agregar la sede {sede.nombre}")
            cantidades["sedes"] += 1
        sedes[clave] = sede

    socios = {}
    for clave, datos in SOCIOS.items():
        socio = Socio(*datos)
        existente = buscar_socio_por_dni(socio.dni, nombre_archivo)
        if existente:
            socio.id = existente[0]
        else:
            if not agregar_socio(socio, nombre_archivo):
                raise RuntimeError(f"No se pudo agregar el socio {socio.nombre}")
            cantidades["socios"] += 1
        socios[clave] = socio.id

    libros = {}
    for datos in LIBROS:
        libro = Libro(*datos)
        existente = buscar_libro_por_isbn(libro.isbn, nombre_archivo)
        if existente:
            libro.id = existente[0]
        else:
            if not agregar_libro(libro, nombre_archivo):
                raise RuntimeError(f"No se pudo agregar el libro {libro.titulo}")
            cantidades["libros"] += 1
        libros[libro.isbn] = libro

    ejemplares = {}
    nuevos = set()
    for numero, datos in enumerate(LIBROS, start=1):
        libro = libros[datos[0]]
        otra_sede = "Norte" if numero % 2 else "Sur"
        for clave in ("Centro", otra_sede):
            codigo = f"DEMO-{clave[0]}-{numero:02d}"
            existente = buscar_ejemplar_por_codigo(codigo, nombre_archivo)
            if existente:
                ejemplares[codigo] = existente[0]
                continue
            ejemplar = Ejemplar(codigo, libro, sedes[clave])
            if not agregar_ejemplar(ejemplar, nombre_archivo):
                raise RuntimeError(f"No se pudo agregar el ejemplar {codigo}")
            ejemplares[codigo] = ejemplar.id
            nuevos.add(codigo)
            cantidades["ejemplares"] += 1

    def reserva(socio, codigo, sede):
        if codigo not in nuevos:
            return None
        identificador = _exigir(registrar_reserva(
            socios[socio], ejemplares[codigo], sedes[sede].id, nombre_archivo
        ), f"reservar {codigo}")
        cantidades["reservas"] += 1
        return identificador

    # Una reserva activa, una que se convierte en préstamo y una cancelada.
    reserva("Ana", "DEMO-C-01", "Centro")
    reserva("Juan", "DEMO-N-01", "Norte")
    cancelada = reserva("Lucía", "DEMO-C-02", "Centro")
    if cancelada is not None:
        _exigir(cancelar_reserva(cancelada, nombre_archivo), "cancelar la reserva de Lucía")

    # Préstamo local activo que cumple la reserva de Juan.
    if "DEMO-N-01" in nuevos:
        _exigir(registrar_prestamo_local(
            socios["Juan"], ejemplares["DEMO-N-01"], sedes["Norte"].id,
            dias=7, nombre_archivo=nombre_archivo
        ), "prestar el ejemplar reservado")
        cantidades["prestamos"] += 1

    # Devolución con daño: queda BAJA/DANADO para probar la reparación.
    if "DEMO-S-02" in nuevos:
        devuelto = _exigir(registrar_prestamo_local(
            socios["Valentina"], ejemplares["DEMO-S-02"], sedes["Sur"].id,
            dias=7, nombre_archivo=nombre_archivo
        ), "prestar el ejemplar que se devolverá dañado")
        _exigir(registrar_devolucion(devuelto, "DANADO", nombre_archivo),
                "devolver el ejemplar dañado")
        cantidades["prestamos"] += 1

    # Interbibliotecario pendiente: remito PREPARADO para despachar en el oral.
    if "DEMO-C-03" in nuevos:
        pendiente = _exigir(solicitar_prestamo_interbibliotecario(
            socios["Sofía"], ejemplares["DEMO-C-03"], sedes["Norte"].id,
            nombre_archivo
        ), "solicitar el primer préstamo interbibliotecario")
        _exigir(crear_remito(pendiente, "DEMO-IDA-001", nombre_archivo),
                "crear el remito pendiente")
        cantidades["prestamos"] += 1
        cantidades["remitos"] += 1

    # Interbibliotecario completo: remito con historial y préstamo ACTIVO.
    if "DEMO-N-03" in nuevos:
        recibido = _exigir(solicitar_prestamo_interbibliotecario(
            socios["Mateo"], ejemplares["DEMO-N-03"], sedes["Sur"].id,
            nombre_archivo
        ), "solicitar el segundo préstamo interbibliotecario")
        remito = _exigir(crear_remito(recibido, "DEMO-IDA-002", nombre_archivo),
                         "crear el remito recibido")
        for estado in ("DESPACHADO", "EN_TRANSITO", "RECIBIDO"):
            _exigir(cambiar_estado_remito(remito, estado, nombre_archivo=nombre_archivo),
                    f"pasar el remito a {estado}")
        _exigir(activar_prestamo_interbibliotecario(
            recibido, dias=14, nombre_archivo=nombre_archivo
        ), "activar el préstamo interbibliotecario")
        cantidades["prestamos"] += 1
        cantidades["remitos"] += 1

    return cantidades


def main():
    parser = argparse.ArgumentParser(description="Cargar datos ficticios de demostración")
    parser.add_argument("--bd", default=ARCHIVO_BD,
                        help=f"Archivo SQLite de destino (predeterminado: {ARCHIVO_BD})")
    opciones = parser.parse_args()

    try:
        cantidades = cargar_datos_demo(opciones.bd)
        print("Datos de demostración cargados:")
        for tipo, cantidad in cantidades.items():
            print(f"  {tipo}: {cantidad} nuevos")
        if not any(cantidades.values()):
            print("Los ejemplos ya estaban cargados. No se modificó nada.")
        print("Listo. Abrí la biblioteca con: python main.py")
    finally:
        DatabaseSingleton(opciones.bd).close_connection()


if __name__ == "__main__":
    main()
