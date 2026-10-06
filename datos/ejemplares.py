from datos.base_datos import conectar, ARCHIVO_BD


def buscar_ejemplar_por_codigo(codigo, nombre_archivo=ARCHIVO_BD):
    conexion = conectar(nombre_archivo)
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT id, codigo, libro_id, sede_pertenencia_id, sede_actual_id,
               estado, estado_fisico
        FROM ejemplares
        WHERE codigo = ?
    """, (codigo,))
    ejemplar = cursor.fetchone()
    conexion.close()
    return ejemplar


def agregar_ejemplar(ejemplar, nombre_archivo=ARCHIVO_BD):
    if buscar_ejemplar_por_codigo(ejemplar.codigo, nombre_archivo) is not None:
        return False

    conexion = conectar(nombre_archivo)
    cursor = conexion.cursor()
    cursor.execute("""
        INSERT INTO ejemplares (
            codigo, libro_id, sede_pertenencia_id, sede_actual_id,
            estado, estado_fisico
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (ejemplar.codigo, ejemplar.libro.id, ejemplar.sede_pertenencia.id,
          ejemplar.sede_actual.id, ejemplar.estado, ejemplar.estado_fisico))
    ejemplar.id = cursor.lastrowid
    conexion.commit()
    conexion.close()
    return True


def listar_ejemplares(nombre_archivo=ARCHIVO_BD):
    conexion = conectar(nombre_archivo)
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT e.id, e.codigo, l.titulo, sp.nombre, sa.nombre,
               e.estado, e.estado_fisico
        FROM ejemplares e
        JOIN libros l ON l.id = e.libro_id
        JOIN sedes sp ON sp.id = e.sede_pertenencia_id
        JOIN sedes sa ON sa.id = e.sede_actual_id
        ORDER BY l.titulo, e.codigo
    """)
    ejemplares = cursor.fetchall()
    conexion.close()
    return ejemplares


def cambiar_estado_ejemplar(id_ejemplar, estado, nombre_archivo=ARCHIVO_BD):
    conexion = conectar(nombre_archivo)
    cursor = conexion.cursor()
    cursor.execute("""
        UPDATE ejemplares
        SET estado = ?
        WHERE id = ?
    """, (estado, id_ejemplar))
    conexion.commit()
    modificadas = cursor.rowcount
    conexion.close()
    return modificadas > 0


def cambiar_estado_fisico_ejemplar(id_ejemplar, estado_fisico, nombre_archivo=ARCHIVO_BD):
    conexion = conectar(nombre_archivo)
    cursor = conexion.cursor()
    cursor.execute("""
        UPDATE ejemplares
        SET estado_fisico = ?
        WHERE id = ?
    """, (estado_fisico, id_ejemplar))
    conexion.commit()
    modificadas = cursor.rowcount
    conexion.close()
    return modificadas > 0
