from datos.base_datos import conectar, ARCHIVO_BD


def buscar_socio_por_dni(dni, nombre_archivo=ARCHIVO_BD):
    conexion = conectar(nombre_archivo)
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT id, dni, nombre, apellido, telefono, email, habilitado
        FROM socios
        WHERE dni = ?
    """, (dni,))
    socio = cursor.fetchone()
    conexion.close()
    return socio


def agregar_socio(socio, nombre_archivo=ARCHIVO_BD):
    if buscar_socio_por_dni(socio.dni, nombre_archivo) is not None:
        return False

    conexion = conectar(nombre_archivo)
    cursor = conexion.cursor()
    cursor.execute("""
        INSERT INTO socios (dni, nombre, apellido, telefono, email, habilitado)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (socio.dni, socio.nombre, socio.apellido, socio.telefono,
          socio.email, int(socio.habilitado)))
    socio.id = cursor.lastrowid
    conexion.commit()
    conexion.close()
    return True


def listar_socios(nombre_archivo=ARCHIVO_BD):
    conexion = conectar(nombre_archivo)
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT id, dni, nombre, apellido, telefono, email, habilitado
        FROM socios
        ORDER BY apellido, nombre
    """)
    socios = cursor.fetchall()
    conexion.close()
    return socios


def modificar_socio(socio, nombre_archivo=ARCHIVO_BD):
    conexion = conectar(nombre_archivo)
    cursor = conexion.cursor()
    cursor.execute("""
        UPDATE socios
        SET nombre = ?, apellido = ?, telefono = ?, email = ?
        WHERE id = ?
    """, (socio.nombre, socio.apellido, socio.telefono, socio.email, socio.id))
    conexion.commit()
    modificadas = cursor.rowcount
    conexion.close()
    return modificadas > 0


def cambiar_habilitacion_socio(id_socio, habilitado, nombre_archivo=ARCHIVO_BD):
    conexion = conectar(nombre_archivo)
    cursor = conexion.cursor()
    cursor.execute("""
        UPDATE socios
        SET habilitado = ?
        WHERE id = ?
    """, (int(habilitado), id_socio))
    conexion.commit()
    modificadas = cursor.rowcount
    conexion.close()
    return modificadas > 0
