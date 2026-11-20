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
    return socios


def modificar_socio(socio, nombre_archivo=ARCHIVO_BD):
    existente = buscar_socio_por_dni(socio.dni, nombre_archivo)
    if existente is not None and existente[0] != socio.id:
        return False

    conexion = conectar(nombre_archivo)
    cursor = conexion.cursor()
    cursor.execute("""
        UPDATE socios
        SET dni = ?, nombre = ?, apellido = ?, telefono = ?, email = ?
        WHERE id = ?
    """, (socio.dni, socio.nombre, socio.apellido, socio.telefono,
          socio.email, socio.id))
    conexion.commit()
    modificadas = cursor.rowcount
    return modificadas > 0


def cambiar_habilitacion_socio(id_socio, habilitado, nombre_archivo=ARCHIVO_BD):
    """Al inhabilitar a un socio se cancelan sus reservas activas, para que
    los ejemplares reservados vuelvan a estar disponibles para otros."""
    conexion = conectar(nombre_archivo)
    cursor = conexion.cursor()
    try:
        cursor.execute("""
            UPDATE socios
            SET habilitado = ?
            WHERE id = ?
        """, (int(habilitado), id_socio))
        modificadas = cursor.rowcount

        if modificadas > 0 and not habilitado:
            cursor.execute("""
                UPDATE ejemplares
                SET estado = 'DISPONIBLE'
                WHERE estado = 'RESERVADO' AND id IN (
                    SELECT ejemplar_id FROM reservas
                    WHERE socio_id = ? AND estado = 'ACTIVA'
                )
            """, (id_socio,))
            cursor.execute("""
                UPDATE reservas
                SET estado = 'CANCELADA'
                WHERE socio_id = ? AND estado = 'ACTIVA'
            """, (id_socio,))

        conexion.commit()
        return modificadas > 0
    except Exception:
        conexion.rollback()
        raise
