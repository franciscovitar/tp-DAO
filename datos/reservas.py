from datetime import date

from datos.base_datos import conectar, ARCHIVO_BD
from datos.prestamos import _tiene_prestamos_vencidos


def registrar_reserva(id_socio, id_ejemplar, id_sede,
                       nombre_archivo=ARCHIVO_BD):
    conexion = conectar(nombre_archivo)
    cursor = conexion.cursor()

    cursor.execute("SELECT habilitado FROM socios WHERE id = ?", (id_socio,))
    socio = cursor.fetchone()
    if socio is None:
        return False, "Socio inexistente"
    if socio[0] == 0:
        return False, "El socio está inhabilitado"
    if _tiene_prestamos_vencidos(cursor, id_socio):
        return False, "El socio tiene préstamos vencidos sin devolver"

    cursor.execute("SELECT activa FROM sedes WHERE id = ?", (id_sede,))
    sede = cursor.fetchone()
    if sede is None:
        return False, "Sede inexistente"
    if sede[0] == 0:
        return False, "La sede está dada de baja"

    cursor.execute("""
        SELECT estado, sede_pertenencia_id, sede_actual_id
        FROM ejemplares
        WHERE id = ?
    """, (id_ejemplar,))
    ejemplar = cursor.fetchone()
    if ejemplar is None:
        return False, "Ejemplar inexistente"
    if ejemplar[0] != "DISPONIBLE":
        return False, "El ejemplar no está disponible"
    if ejemplar[1] != id_sede or ejemplar[2] != id_sede:
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
        return True, id_reserva
    except Exception:
        conexion.rollback()
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
        return False, "Reserva inexistente"
    if reserva[1] != "ACTIVA":
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
        return True, "Reserva cancelada"
    except Exception:
        conexion.rollback()
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
    return reserva


def listar_reservas(nombre_archivo=ARCHIVO_BD):
    conexion = conectar(nombre_archivo)
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT r.id, s.dni, s.nombre || ' ' || s.apellido,
               l.titulo, e.codigo, se.nombre, r.fecha, r.estado
        FROM reservas r
        JOIN socios s ON s.id = r.socio_id
        JOIN ejemplares e ON e.id = r.ejemplar_id
        JOIN libros l ON l.id = e.libro_id
        JOIN sedes se ON se.id = r.sede_id
        ORDER BY r.id DESC
    """)
    reservas = cursor.fetchall()
    return reservas
