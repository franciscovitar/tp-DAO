from datetime import date, timedelta

from datos.base_datos import conectar, ARCHIVO_BD


def registrar_prestamo_local(id_socio, id_ejemplar, id_sede, dias=14,
                              nombre_archivo=ARCHIVO_BD):
    conexion = conectar(nombre_archivo)
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT habilitado
        FROM socios
        WHERE id = ?
    """, (id_socio,))
    socio = cursor.fetchone()
    if socio is None:
        conexion.close()
        return False, "Socio inexistente"
    if socio[0] == 0:
        conexion.close()
        return False, "El socio está inhabilitado"

    cursor.execute("""
        SELECT activa
        FROM sedes
        WHERE id = ?
    """, (id_sede,))
    sede = cursor.fetchone()
    if sede is None:
        conexion.close()
        return False, "Sede inexistente"
    if sede[0] == 0:
        conexion.close()
        return False, "La sede está dada de baja"

    cursor.execute("""
        SELECT estado, sede_pertenencia_id, sede_actual_id
        FROM ejemplares
        WHERE id = ?
    """, (id_ejemplar,))
    ejemplar = cursor.fetchone()
    if ejemplar is None:
        conexion.close()
        return False, "Ejemplar inexistente"

    reserva_activa = None
    if ejemplar[0] == "RESERVADO":
        cursor.execute("""
            SELECT id, socio_id
            FROM reservas
            WHERE ejemplar_id = ? AND estado = ?
        """, (id_ejemplar, "ACTIVA"))
        reserva_activa = cursor.fetchone()
        if reserva_activa is None or reserva_activa[1] != id_socio:
            conexion.close()
            return False, "El ejemplar está reservado para otro socio"
    elif ejemplar[0] != "DISPONIBLE":
        conexion.close()
        return False, "El ejemplar no está disponible"

    if ejemplar[1] != id_sede:
        conexion.close()
        return False, "El ejemplar no pertenece a la sede de origen"
    if ejemplar[2] != id_sede:
        conexion.close()
        return False, "El ejemplar no se encuentra en la sede de origen"

    hoy = date.today()
    vencimiento = hoy + timedelta(days=dias)

    try:
        cursor.execute("""
            INSERT INTO prestamos (
                socio_id, ejemplar_id, sede_origen_id, sede_destino_id,
                fecha_solicitud, fecha_inicio, fecha_vencimiento,
                fecha_devolucion, estado
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (id_socio, id_ejemplar, id_sede, id_sede,
              hoy.isoformat(), hoy.isoformat(), vencimiento.isoformat(),
              None, "ACTIVO"))
        id_prestamo = cursor.lastrowid

        cursor.execute("""
            UPDATE ejemplares
            SET estado = ?
            WHERE id = ?
        """, ("PRESTADO", id_ejemplar))

        if reserva_activa is not None:
            cursor.execute("""
                UPDATE reservas
                SET estado = ?
                WHERE id = ?
            """, ("CUMPLIDA", reserva_activa[0]))

        conexion.commit()
        conexion.close()
        return True, id_prestamo
    except Exception:
        conexion.rollback()
        conexion.close()
        raise


def registrar_devolucion(id_prestamo, estado_fisico="BUENO",
                          nombre_archivo=ARCHIVO_BD):
    conexion = conectar(nombre_archivo)
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT ejemplar_id, estado
        FROM prestamos
        WHERE id = ?
    """, (id_prestamo,))
    prestamo = cursor.fetchone()

    if prestamo is None:
        conexion.close()
        return False, "Préstamo inexistente"
    if prestamo[1] != "ACTIVO":
        conexion.close()
        return False, "El préstamo no está activo"

    hoy = date.today().isoformat()

    try:
        cursor.execute("""
            UPDATE prestamos
            SET fecha_devolucion = ?, estado = ?
            WHERE id = ?
        """, (hoy, "DEVUELTO", id_prestamo))

        cursor.execute("""
            UPDATE ejemplares
            SET estado = ?, estado_fisico = ?
            WHERE id = ?
        """, ("DISPONIBLE", estado_fisico, prestamo[0]))

        conexion.commit()
        conexion.close()
        return True, "Devolución registrada"
    except Exception:
        conexion.rollback()
        conexion.close()
        raise


def buscar_prestamo(id_prestamo, nombre_archivo=ARCHIVO_BD):
    conexion = conectar(nombre_archivo)
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT id, socio_id, ejemplar_id, sede_origen_id, sede_destino_id,
               fecha_solicitud, fecha_inicio, fecha_vencimiento,
               fecha_devolucion, estado
        FROM prestamos
        WHERE id = ?
    """, (id_prestamo,))
    prestamo = cursor.fetchone()
    conexion.close()
    return prestamo
