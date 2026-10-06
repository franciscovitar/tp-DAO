import sqlite3

ARCHIVO_BD = "biblioteca.db"


def conectar(nombre_archivo=ARCHIVO_BD):
    conexion = sqlite3.connect(nombre_archivo)
    conexion.execute("PRAGMA foreign_keys = ON")
    return conexion


def crear_tablas(nombre_archivo=ARCHIVO_BD):
    conexion = conectar(nombre_archivo)
    cursor = conexion.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sedes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            direccion TEXT NOT NULL,
            telefono TEXT,
            email TEXT,
            horario TEXT,
            activa INTEGER NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS socios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dni TEXT NOT NULL UNIQUE,
            nombre TEXT NOT NULL,
            apellido TEXT NOT NULL,
            telefono TEXT,
            email TEXT,
            habilitado INTEGER NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS libros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            isbn TEXT NOT NULL UNIQUE,
            titulo TEXT NOT NULL,
            autor TEXT NOT NULL,
            editorial TEXT,
            anio INTEGER
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ejemplares (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT NOT NULL UNIQUE,
            libro_id INTEGER NOT NULL,
            sede_pertenencia_id INTEGER NOT NULL,
            sede_actual_id INTEGER NOT NULL,
            estado TEXT NOT NULL,
            estado_fisico TEXT NOT NULL,
            FOREIGN KEY (libro_id) REFERENCES libros(id),
            FOREIGN KEY (sede_pertenencia_id) REFERENCES sedes(id),
            FOREIGN KEY (sede_actual_id) REFERENCES sedes(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS prestamos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            socio_id INTEGER NOT NULL,
            ejemplar_id INTEGER NOT NULL,
            sede_origen_id INTEGER NOT NULL,
            sede_destino_id INTEGER NOT NULL,
            fecha_solicitud TEXT NOT NULL,
            fecha_inicio TEXT,
            fecha_vencimiento TEXT,
            fecha_devolucion TEXT,
            estado TEXT NOT NULL,
            FOREIGN KEY (socio_id) REFERENCES socios(id),
            FOREIGN KEY (ejemplar_id) REFERENCES ejemplares(id),
            FOREIGN KEY (sede_origen_id) REFERENCES sedes(id),
            FOREIGN KEY (sede_destino_id) REFERENCES sedes(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reservas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            socio_id INTEGER NOT NULL,
            ejemplar_id INTEGER NOT NULL,
            sede_id INTEGER NOT NULL,
            fecha TEXT NOT NULL,
            estado TEXT NOT NULL,
            FOREIGN KEY (socio_id) REFERENCES socios(id),
            FOREIGN KEY (ejemplar_id) REFERENCES ejemplares(id),
            FOREIGN KEY (sede_id) REFERENCES sedes(id)
        )
    """)

    conexion.commit()
    conexion.close()
