from datetime import date

from datos.base_datos import conectar, ARCHIVO_BD


def registrar_reserva(id_socio, id_ejemplar, id_sede,
                       nombre_archivo=ARCHIVO_BD):
    conexion = conectar(nombre_archivo)
    cursor = conexion.cursor()

    cursor.execute("SELECT habilitado FROM socios WHERE id = ?", (id_socio,))
    socio = cursor.fetchone()
    if socio is None:
        conexion.close()
        return False, "Socio inexistente"
    if socio[0] == 0:
        conexion.close()
        return False, "El socio está inhabilitado"

    cursor.execute("SELECT activa FROM sedes WHERE id = ?", (id_sede,))
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
    if ejemplar[0] != "DISPONIBLE":
        conexion.close()
        return False, "El ejemplar no está disponible"
    if ejemplar[1] != id_sede or ejemplar[2] != id_sede:
        conexion.close()
        return False, "El ejemplar no se encuentra disponible en esa sede"

    try:
        cursor.execute("""
            INSERT INTO reservas (socio_id, ejemplar_id, sede_id, fecha, estado)
            VALUES (?, ?, ?, ?, ?)
        """, (id_socio, id_ejemplar, id_sede, date.today().isoformat(), "ACTIVA"))
        id_reserva = cursor.lastrowid

        cursor.execute("""
            UPDATE ejemplares
            SET estado = ?
            WHERE id = ?
        """, ("RESERVADO", id_ejemplar))

        conexion.commit()
        conexion.close()
        return True, id_reserva
    except Exception:
        conexion.rollback()
        conexion.close()
        raise


def cancelar_reserva(id_reserva, nombre_archivo=ARCHIVO_BD):
    conexion = conectar(nombre_archivo)
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT ejemplar_id, estado
        FROM reservas
        WHERE id = ?
    """, (id_reserva,))
    reserva = cursor.fetchone()

    if reserva is None:
        conexion.close()
        return False, "Reserva inexistente"
    if reserva[1] != "ACTIVA":
        conexion.close()
        return False, "La reserva no está activa"

    try:
        cursor.execute("""
            UPDATE reservas
            SET estado = ?
            WHERE id = ?
        """, ("CANCELADA", id_reserva))

        cursor.execute("""
            UPDATE ejemplares
            SET estado = ?
            WHERE id = ?
        """, ("DISPONIBLE", reserva[0]))

        conexion.commit()
        conexion.close()
        return True, "Reserva cancelada"
    except Exception:
        conexion.rollback()
        conexion.close()
        raise


def buscar_reserva(id_reserva, nombre_archivo=ARCHIVO_BD):
    conexion = conectar(nombre_archivo)
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT id, socio_id, ejemplar_id, sede_id, fecha, estado
        FROM reservas
        WHERE id = ?
    """, (id_reserva,))
    reserva = cursor.fetchone()
    conexion.close()
    return reserva
