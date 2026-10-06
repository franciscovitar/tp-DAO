from datos.base_datos import conectar, ARCHIVO_BD


def prestamos_activos_y_material_en_transito(nombre_archivo=ARCHIVO_BD):
    conexion = conectar(nombre_archivo)
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT p.id, s.dni, s.nombre, s.apellido, l.titulo,
               e.codigo, so.nombre, sd.nombre, p.fecha_vencimiento
        FROM prestamos p
        JOIN socios s ON s.id = p.socio_id
        JOIN ejemplares e ON e.id = p.ejemplar_id
        JOIN libros l ON l.id = e.libro_id
        JOIN sedes so ON so.id = p.sede_origen_id
        JOIN sedes sd ON sd.id = p.sede_destino_id
        WHERE p.estado = 'ACTIVO'
        ORDER BY p.id
    """)
    prestamos = cursor.fetchall()

    cursor.execute("""
        SELECT r.numero, l.titulo, e.codigo, so.nombre, sd.nombre, r.estado
        FROM remitos r
        JOIN remito_ejemplares re ON re.remito_id = r.id
        JOIN ejemplares e ON e.id = re.ejemplar_id
        JOIN libros l ON l.id = e.libro_id
        JOIN sedes so ON so.id = r.sede_origen_id
        JOIN sedes sd ON sd.id = r.sede_destino_id
        WHERE r.estado IN ('DESPACHADO', 'EN_TRANSITO')
        ORDER BY r.id
    """)
    en_transito = cursor.fetchall()
    conexion.close()
    return {"prestamos_activos": prestamos, "material_en_transito": en_transito}


def libros_mas_solicitados_interbibliotecarios(nombre_archivo=ARCHIVO_BD):
    conexion = conectar(nombre_archivo)
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT l.isbn, l.titulo, COUNT(*) AS cantidad
        FROM prestamos p
        JOIN ejemplares e ON e.id = p.ejemplar_id
        JOIN libros l ON l.id = e.libro_id
        WHERE p.sede_origen_id <> p.sede_destino_id
        GROUP BY l.id, l.isbn, l.titulo
        ORDER BY cantidad DESC, l.titulo
    """)
    resultado = cursor.fetchall()
    conexion.close()
    return resultado


def disponibilidad_catalogo_por_sede(nombre_archivo=ARCHIVO_BD):
    conexion = conectar(nombre_archivo)
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT s.nombre, l.isbn, l.titulo, COUNT(*) AS disponibles
        FROM ejemplares e
        JOIN sedes s ON s.id = e.sede_actual_id
        JOIN libros l ON l.id = e.libro_id
        WHERE e.estado = 'DISPONIBLE'
        GROUP BY s.id, s.nombre, l.id, l.isbn, l.titulo
        ORDER BY s.nombre, l.titulo
    """)
    resultado = cursor.fetchall()
    conexion.close()
    return resultado


def movimientos_y_tiempo_promedio_transito(nombre_archivo=ARCHIVO_BD):
    conexion = conectar(nombre_archivo)
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT so.nombre, sd.nombre, COUNT(*) AS cantidad
        FROM remitos r
        JOIN sedes so ON so.id = r.sede_origen_id
        JOIN sedes sd ON sd.id = r.sede_destino_id
        GROUP BY so.id, so.nombre, sd.id, sd.nombre
        ORDER BY cantidad DESC, so.nombre, sd.nombre
    """)
    movimientos = cursor.fetchall()

    cursor.execute("""
        SELECT AVG((julianday(fecha_recepcion) - julianday(fecha_despacho)) * 24)
        FROM remitos
        WHERE estado = 'RECIBIDO'
          AND fecha_despacho IS NOT NULL
          AND fecha_recepcion IS NOT NULL
    """)
    promedio = cursor.fetchone()[0]
    conexion.close()
    return {
        "movimientos": movimientos,
        "horas_promedio_transito": 0 if promedio is None else promedio
    }


def prestamos_vencidos(nombre_archivo=ARCHIVO_BD):
    conexion = conectar(nombre_archivo)
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT p.id, s.dni, s.nombre || ' ' || s.apellido,
               l.titulo, e.codigo, p.fecha_vencimiento
        FROM prestamos p
        JOIN socios s ON s.id = p.socio_id
        JOIN ejemplares e ON e.id = p.ejemplar_id
        JOIN libros l ON l.id = e.libro_id
        WHERE p.estado = 'ACTIVO'
          AND date(p.fecha_vencimiento) < date('now')
        ORDER BY p.fecha_vencimiento
    """)
    vencidos = cursor.fetchall()
    conexion.close()
    return vencidos
