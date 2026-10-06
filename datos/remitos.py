from datetime import datetime

from datos.base_datos import conectar, ARCHIVO_BD
from modelos.remito import Remito


def crear_remito(id_prestamo, numero, nombre_archivo=ARCHIVO_BD):
    conexion = conectar(nombre_archivo)
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT ejemplar_id, sede_origen_id, sede_destino_id, estado
        FROM prestamos
        WHERE id = ?
    """, (id_prestamo,))
    prestamo = cursor.fetchone()
    if prestamo is None:
        conexion.close()
        return False, "Préstamo inexistente"
    if prestamo[3] != "SOLICITADO":
        conexion.close()
        return False, "El préstamo no está pendiente de envío"

    cursor.execute("SELECT activa FROM sedes WHERE id = ?", (prestamo[1],))
    origen = cursor.fetchone()
    cursor.execute("SELECT activa FROM sedes WHERE id = ?", (prestamo[2],))
    destino = cursor.fetchone()
    if origen is None or origen[0] == 0:
        conexion.close()
        return False, "La sede origen está dada de baja"
    if destino is None or destino[0] == 0:
        conexion.close()
        return False, "La sede destino está dada de baja"

    cursor.execute("""
        SELECT estado, sede_pertenencia_id, sede_actual_id
        FROM ejemplares
        WHERE id = ?
    """, (prestamo[0],))
    ejemplar = cursor.fetchone()
    if ejemplar is None:
        conexion.close()
        return False, "Ejemplar inexistente"
    if ejemplar[0] != "RESERVADO":
        conexion.close()
        return False, "El ejemplar no está reservado para el envío"
    if ejemplar[1] != prestamo[1] or ejemplar[2] != prestamo[1]:
        conexion.close()
        return False, "El ejemplar no se encuentra en la sede de origen"

    cursor.execute("SELECT id FROM remitos WHERE numero = ?", (numero,))
    if cursor.fetchone() is not None:
        conexion.close()
        return False, "Ya existe un remito con ese número"

    ahora = datetime.now().isoformat(timespec="seconds")

    try:
        cursor.execute("""
            INSERT INTO remitos (
                numero, prestamo_id, sede_origen_id, sede_destino_id,
                fecha_creacion, fecha_despacho, fecha_recepcion, estado
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (numero, id_prestamo, prestamo[1], prestamo[2],
              ahora, None, None, "PREPARADO"))
        id_remito = cursor.lastrowid

        cursor.execute("""
            INSERT INTO remito_ejemplares (remito_id, ejemplar_id)
            VALUES (?, ?)
        """, (id_remito, prestamo[0]))

        cursor.execute("""
            INSERT INTO historial_remito (remito_id, estado, fecha_hora)
            VALUES (?, ?, ?)
        """, (id_remito, "PREPARADO", ahora))

        conexion.commit()
        conexion.close()
        return True, id_remito
    except Exception:
        conexion.rollback()
        conexion.close()
        raise


def cambiar_estado_remito(id_remito, nuevo_estado, observadores=None,
                            nombre_archivo=ARCHIVO_BD):
    conexion = conectar(nombre_archivo)
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT id, numero, sede_origen_id, sede_destino_id,
               fecha_creacion, fecha_despacho, fecha_recepcion, estado
        FROM remitos
        WHERE id = ?
    """, (id_remito,))
    fila = cursor.fetchone()
    if fila is None:
        conexion.close()
        return False, "Remito inexistente"

    remito = Remito(
        fila[1], fila[2], fila[3],
        fecha_creacion=fila[4],
        fecha_despacho=fila[5],
        fecha_recepcion=fila[6],
        estado=fila[7], id=fila[0]
    )

    if observadores is not None:
        for observer in observadores:
            remito.attach(observer)

    if not remito.cambiar_estado(nuevo_estado):
        conexion.close()
        return False, "Cambio de estado no permitido"

    ahora = datetime.now().isoformat(timespec="seconds")

    try:
        fecha_despacho = fila[5]
        fecha_recepcion = fila[6]
        if nuevo_estado == "DESPACHADO":
            fecha_despacho = ahora
        elif nuevo_estado == "RECIBIDO":
            fecha_recepcion = ahora

        cursor.execute("""
            UPDATE remitos
            SET estado = ?, fecha_despacho = ?, fecha_recepcion = ?
            WHERE id = ?
        """, (nuevo_estado, fecha_despacho, fecha_recepcion, id_remito))

        cursor.execute("""
            INSERT INTO historial_remito (remito_id, estado, fecha_hora)
            VALUES (?, ?, ?)
        """, (id_remito, nuevo_estado, ahora))

        if nuevo_estado == "DESPACHADO":
            cursor.execute("""
                UPDATE ejemplares
                SET estado = 'EN_TRANSITO'
                WHERE id IN (
                    SELECT ejemplar_id
                    FROM remito_ejemplares
                    WHERE remito_id = ?
                )
            """, (id_remito,))
        elif nuevo_estado == "RECIBIDO":
            cursor.execute("""
                UPDATE ejemplares
                SET estado = 'RESERVADO', sede_actual_id = ?
                WHERE id IN (
                    SELECT ejemplar_id
                    FROM remito_ejemplares
                    WHERE remito_id = ?
                )
            """, (fila[3], id_remito))

        conexion.commit()
        conexion.close()
        return True, "Estado actualizado"
    except Exception:
        conexion.rollback()
        conexion.close()
        raise


def buscar_remito(id_remito, nombre_archivo=ARCHIVO_BD):
    conexion = conectar(nombre_archivo)
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT id, numero, prestamo_id, sede_origen_id, sede_destino_id,
               fecha_creacion, fecha_despacho, fecha_recepcion, estado
        FROM remitos
        WHERE id = ?
    """, (id_remito,))
    remito = cursor.fetchone()
    conexion.close()
    return remito


def listar_historial_remito(id_remito, nombre_archivo=ARCHIVO_BD):
    conexion = conectar(nombre_archivo)
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT estado, fecha_hora
        FROM historial_remito
        WHERE remito_id = ?
        ORDER BY id
    """, (id_remito,))
    historial = cursor.fetchall()
    conexion.close()
    return historial


def listar_remitos(nombre_archivo=ARCHIVO_BD):
    conexion = conectar(nombre_archivo)
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT r.id, r.numero, r.prestamo_id, so.nombre, sd.nombre,
               r.fecha_creacion, r.fecha_despacho, r.fecha_recepcion, r.estado
        FROM remitos r
        JOIN sedes so ON so.id = r.sede_origen_id
        JOIN sedes sd ON sd.id = r.sede_destino_id
        ORDER BY r.id DESC
    """)
    remitos = cursor.fetchall()
    conexion.close()
    return remitos
