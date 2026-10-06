from datos.base_datos import conectar, ARCHIVO_BD


def agregar_sede(sede, nombre_archivo=ARCHIVO_BD):
    conexion = conectar(nombre_archivo)
    cursor = conexion.cursor()
    cursor.execute("""
        INSERT INTO sedes (nombre, direccion, telefono, email, horario, activa)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (sede.nombre, sede.direccion, sede.telefono, sede.email,
          sede.horario, int(sede.activa)))
    sede.id = cursor.lastrowid
    conexion.commit()
    conexion.close()
    return sede.id


def listar_sedes(nombre_archivo=ARCHIVO_BD):
    conexion = conectar(nombre_archivo)
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT id, nombre, direccion, telefono, email, horario, activa
        FROM sedes
        ORDER BY nombre
    """)
    sedes = cursor.fetchall()
    conexion.close()
    return sedes


def buscar_sede(id_sede, nombre_archivo=ARCHIVO_BD):
    conexion = conectar(nombre_archivo)
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT id, nombre, direccion, telefono, email, horario, activa
        FROM sedes
        WHERE id = ?
    """, (id_sede,))
    sede = cursor.fetchone()
    conexion.close()
    return sede


def modificar_sede(sede, nombre_archivo=ARCHIVO_BD):
    conexion = conectar(nombre_archivo)
    cursor = conexion.cursor()
    cursor.execute("""
        UPDATE sedes
        SET nombre = ?, direccion = ?, telefono = ?, email = ?, horario = ?
        WHERE id = ?
    """, (sede.nombre, sede.direccion, sede.telefono, sede.email,
          sede.horario, sede.id))
    conexion.commit()
    modificadas = cursor.rowcount
    conexion.close()
    return modificadas > 0


def cambiar_estado_sede(id_sede, activa, nombre_archivo=ARCHIVO_BD):
    conexion = conectar(nombre_archivo)
    cursor = conexion.cursor()
    cursor.execute("""
        UPDATE sedes
        SET activa = ?
        WHERE id = ?
    """, (int(activa), id_sede))
    conexion.commit()
    modificadas = cursor.rowcount
    conexion.close()
    return modificadas > 0
