from datetime import datetime

from datos.base_datos import conectar, ARCHIVO_BD
from modelos.remito import Remito
from patrones.observer import HistorialRemitoObserver


def crear_remito(id_prestamo, numero, nombre_archivo=ARCHIVO_BD):
    if numero.strip() == "":
        return False, "Número de remito obligatorio"

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

    cursor.execute("""
        SELECT id FROM remitos
        WHERE prestamo_id = ? AND sede_origen_id = ? AND sede_destino_id = ?
    """, (id_prestamo, prestamo[1], prestamo[2]))
    if cursor.fetchone() is not None:
        conexion.close()
        return False, "El préstamo ya tiene un remito de ida"

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


def crear_remito_retorno(id_prestamo, numero, nombre_archivo=ARCHIVO_BD):
    if numero.strip() == "":
        return False, "Número de remito obligatorio"

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
    if prestamo[3] != "DEVUELTO":
        conexion.close()
        return False, "El préstamo todavía no fue devuelto"
    if prestamo[1] == prestamo[2]:
        conexion.close()
        return False, "El préstamo es local y no necesita remito de retorno"

    id_sede_origen = prestamo[2]
    id_sede_destino = prestamo[1]

    cursor.execute("SELECT activa FROM sedes WHERE id = ?", (id_sede_origen,))
    origen = cursor.fetchone()
    cursor.execute("SELECT activa FROM sedes WHERE id = ?", (id_sede_destino,))
    destino = cursor.fetchone()
    if origen is None or origen[0] == 0:
        conexion.close()
        return False, "La sede origen está dada de baja"
    if destino is None or destino[0] == 0:
        conexion.close()
        return False, "La sede destino está dada de baja"

    cursor.execute("SELECT id FROM remitos WHERE numero = ?", (numero,))
    if cursor.fetchone() is not None:
        conexion.close()
        return False, "Ya existe un remito con ese número"

    cursor.execute("""
        SELECT id FROM remitos
        WHERE prestamo_id = ? AND sede_origen_id = ? AND sede_destino_id = ?
    """, (id_prestamo, id_sede_origen, id_sede_destino))
    if cursor.fetchone() is not None:
        conexion.close()
        return False, "El préstamo ya tiene un remito de retorno"

    cursor.execute("""
        SELECT estado, sede_pertenencia_id, sede_actual_id
        FROM ejemplares
        WHERE id = ?
    """, (prestamo[0],))
    ejemplar = cursor.fetchone()
    if ejemplar is None:
        conexion.close()
        return False, "Ejemplar inexistente"
    if ejemplar[0] != "PENDIENTE_RETORNO" or ejemplar[2] != id_sede_origen:
        conexion.close()
        return False, "El ejemplar no está pendiente de retorno en la sede de devolución"
    if ejemplar[1] != id_sede_destino:
        conexion.close()
        return False, "La sede de retorno no coincide con la sede de pertenencia"

    ahora = datetime.now().isoformat(timespec="seconds")

    try:
        cursor.execute("""
            INSERT INTO remitos (
                numero, prestamo_id, sede_origen_id, sede_destino_id,
                fecha_creacion, fecha_despacho, fecha_recepcion, estado
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (numero, id_prestamo, id_sede_origen, id_sede_destino,
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
        SELECT id, numero, prestamo_id, sede_origen_id, sede_destino_id,
               fecha_creacion, fecha_despacho, fecha_recepcion, estado
        FROM remitos
        WHERE id = ?
    """, (id_remito,))
    fila = cursor.fetchone()
    if fila is None:
        conexion.close()
        return False, "Remito inexistente"

    remito = Remito(
        fila[1], fila[3], fila[4],
        fecha_creacion=fila[5],
        fecha_despacho=fila[6],
        fecha_recepcion=fila[7],
        estado=fila[8], id=fila[0]
    )

    historial_observer = HistorialRemitoObserver(cursor)
    remito.attach(historial_observer)

    if observadores is not None:
        for observer in observadores:
            remito.attach(observer)

    try:
        if not remito.cambiar_estado(nuevo_estado):
            conexion.close()
            return False, "Cambio de estado no permitido"

        ahora = datetime.now().isoformat(timespec="seconds")
        fecha_despacho = fila[6]
        fecha_recepcion = fila[7]
        if nuevo_estado == "DESPACHADO":
            fecha_despacho = ahora
        elif nuevo_estado == "RECIBIDO":
            fecha_recepcion = ahora

        cursor.execute("""
            UPDATE remitos
            SET estado = ?, fecha_despacho = ?, fecha_recepcion = ?
            WHERE id = ?
        """, (nuevo_estado, fecha_despacho, fecha_recepcion, id_remito))

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
                SELECT sede_origen_id, sede_destino_id
                FROM prestamos
                WHERE id = ?
            """, (fila[2],))
            prestamo = cursor.fetchone()
            es_retorno = (
                prestamo is not None
                and fila[3] == prestamo[1]
                and fila[4] == prestamo[0]
            )
            estado_ejemplar = "DISPONIBLE" if es_retorno else "RESERVADO"

            cursor.execute("""
                UPDATE ejemplares
                SET estado = ?, sede_actual_id = ?
                WHERE id IN (
                    SELECT ejemplar_id
                    FROM remito_ejemplares
                    WHERE remito_id = ?
                )
            """, (estado_ejemplar, fila[4], id_remito))

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
