from datos.base_datos import conectar, ARCHIVO_BD


def buscar_libro_por_isbn(isbn, nombre_archivo=ARCHIVO_BD):
    conexion = conectar(nombre_archivo)
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT id, isbn, titulo, autor, editorial, anio
        FROM libros
        WHERE isbn = ?
    """, (isbn,))
    libro = cursor.fetchone()
    conexion.close()
    return libro


def agregar_libro(libro, nombre_archivo=ARCHIVO_BD):
    if buscar_libro_por_isbn(libro.isbn, nombre_archivo) is not None:
        return False

    conexion = conectar(nombre_archivo)
    cursor = conexion.cursor()
    cursor.execute("""
        INSERT INTO libros (isbn, titulo, autor, editorial, anio)
        VALUES (?, ?, ?, ?, ?)
    """, (libro.isbn, libro.titulo, libro.autor, libro.editorial, libro.anio))
    libro.id = cursor.lastrowid
    conexion.commit()
    conexion.close()
    return True


def listar_libros(nombre_archivo=ARCHIVO_BD):
    conexion = conectar(nombre_archivo)
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT id, isbn, titulo, autor, editorial, anio
        FROM libros
        ORDER BY titulo
    """)
    libros = cursor.fetchall()
    conexion.close()
    return libros


def modificar_libro(libro, nombre_archivo=ARCHIVO_BD):
    conexion = conectar(nombre_archivo)
    cursor = conexion.cursor()
    cursor.execute("""
        UPDATE libros
        SET titulo = ?, autor = ?, editorial = ?, anio = ?
        WHERE id = ?
    """, (libro.titulo, libro.autor, libro.editorial, libro.anio, libro.id))
    conexion.commit()
    modificadas = cursor.rowcount
    conexion.close()
    return modificadas > 0
