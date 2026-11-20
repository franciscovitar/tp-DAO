from datetime import date, timedelta

from datos.base_datos import conectar, ARCHIVO_BD
from datos.validaciones import validar_dias_prestamo


def _tiene_prestamos_vencidos(cursor, id_socio):
    cursor.execute("""
        SELECT 1 FROM prestamos
        WHERE socio_id = ? AND estado = 'ACTIVO'
          AND date(fecha_vencimiento) < date('now', 'localtime')
    """, (id_socio,))
    return cursor.fetchone() is not None


def registrar_prestamo_local(id_socio, id_ejemplar, id_sede, dias=14,
                              nombre_archivo=ARCHIVO_BD):
    ok, dias = validar_dias_prestamo(dias)
    if not ok:
        return False, dias

    conexion = conectar(nombre_archivo)
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT habilitado
        FROM socios
        WHERE id = ?
    """, (id_socio,))
    socio = cursor.fetchone()
    if socio is None:
        return False, "Socio inexistente"
    if socio[0] == 0:
        return False, "El socio está inhabilitado"
    if _tiene_prestamos_vencidos(cursor, id_socio):
        return False, "El socio tiene préstamos vencidos sin devolver"

    cursor.execute("""
        SELECT activa
        FROM sedes
        WHERE id = ?
    """, (id_sede,))
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

    reserva_activa = None
    if ejemplar[0] == "RESERVADO":
        cursor.execute("""
            SELECT id, socio_id
            FROM reservas
            WHERE ejemplar_id = ? AND estado = ?
        """, (id_ejemplar, "ACTIVA"))
        reserva_activa = cursor.fetchone()
        if reserva_activa is None or reserva_activa[1] != id_socio:
            return False, "El ejemplar está reservado para otro socio"
    elif ejemplar[0] != "DISPONIBLE":
        return False, "El ejemplar no está disponible"

    if ejemplar[1] != id_sede:
        return False, "El ejemplar no pertenece a la sede de origen"
    if ejemplar[2] != id_sede:
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
        return True, id_prestamo
    except Exception:
        conexion.rollback()
        raise


def solicitar_prestamo_interbibliotecario(id_socio, id_ejemplar,
                                            id_sede_destino,
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

    cursor.execute("SELECT activa FROM sedes WHERE id = ?", (id_sede_destino,))
    destino = cursor.fetchone()
    if destino is None:
        return False, "Sede destino inexistente"
    if destino[0] == 0:
        return False, "La sede destino está dada de baja"

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

    id_sede_origen = ejemplar[2]
    if id_sede_origen == id_sede_destino:
        return False, "El ejemplar ya se encuentra en la sede destino"
    if ejemplar[1] != id_sede_origen:
        return False, "El ejemplar no pertenece a la sede de origen"

    cursor.execute("SELECT activa FROM sedes WHERE id = ?", (id_sede_origen,))
    origen = cursor.fetchone()
    if origen is None or origen[0] == 0:
        return False, "La sede origen está dada de baja"

    hoy = date.today().isoformat()

    try:
        cursor.execute("""
            INSERT INTO prestamos (
                socio_id, ejemplar_id, sede_origen_id, sede_destino_id,
                fecha_solicitud, fecha_inicio, fecha_vencimiento,
                fecha_devolucion, estado
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (id_socio, id_ejemplar, id_sede_origen, id_sede_destino,
              hoy, None, None, None, "SOLICITADO"))
        id_prestamo = cursor.lastrowid

        cursor.execute("""
            UPDATE ejemplares
            SET estado = ?
            WHERE id = ?
        """, ("RESERVADO", id_ejemplar))

        conexion.commit()
        return True, id_prestamo
    except Exception:
        conexion.rollback()
        raise


def activar_prestamo_interbibliotecario(id_prestamo, dias=14,
                                          nombre_archivo=ARCHIVO_BD):
    ok, dias = validar_dias_prestamo(dias)
    if not ok:
        return False, dias

    conexion = conectar(nombre_archivo)
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT ejemplar_id, sede_destino_id, estado, socio_id, sede_origen_id
        FROM prestamos
        WHERE id = ?
    """, (id_prestamo,))
    prestamo = cursor.fetchone()
    if prestamo is None:
        return False, "Préstamo inexistente"
    if prestamo[2] != "SOLICITADO":
        return False, "La solicitud no está pendiente"

    # Las sedes pudieron ser dadas de baja durante el traslado.
    for id_sede, tipo in ((prestamo[4], "origen"), (prestamo[1], "destino")):
        cursor.execute("SELECT activa FROM sedes WHERE id = ?", (id_sede,))
        sede = cursor.fetchone()
        if sede is None or sede[0] == 0:
            return False, f"La sede {tipo} está dada de baja"

    cursor.execute("SELECT habilitado FROM socios WHERE id = ?", (prestamo[3],))
    socio = cursor.fetchone()
    if socio is None:
        return False, "Socio inexistente"
    if socio[0] == 0:
        return False, "El socio está inhabilitado"
    if _tiene_prestamos_vencidos(cursor, prestamo[3]):
        return False, "El socio tiene préstamos vencidos sin devolver"

    cursor.execute("""
        SELECT estado, sede_actual_id
        FROM ejemplares
        WHERE id = ?
    """, (prestamo[0],))
    ejemplar = cursor.fetchone()
    if ejemplar[0] != "RESERVADO" or ejemplar[1] != prestamo[1]:
        return False, "El ejemplar todavía no fue recibido en la sede destino"

    hoy = date.today()
    vencimiento = hoy + timedelta(days=dias)

    try:
        cursor.execute("""
            UPDATE prestamos
            SET fecha_inicio = ?, fecha_vencimiento = ?, estado = ?
            WHERE id = ?
        """, (hoy.isoformat(), vencimiento.isoformat(), "ACTIVO", id_prestamo))
        cursor.execute("""
            UPDATE ejemplares
            SET estado = ?
            WHERE id = ?
        """, ("PRESTADO", prestamo[0]))
        conexion.commit()
        return True, "Préstamo activado"
    except Exception:
        conexion.rollback()
        raise


def registrar_devolucion(id_prestamo, estado_fisico="BUENO",
                          nombre_archivo=ARCHIVO_BD):
    if estado_fisico not in ("BUENO", "DANADO"):
        return False, "Estado físico inválido"

    conexion = conectar(nombre_archivo)
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT ejemplar_id, estado, sede_origen_id, sede_destino_id
        FROM prestamos
        WHERE id = ?
    """, (id_prestamo,))
    prestamo = cursor.fetchone()

    if prestamo is None:
        return False, "Préstamo inexistente"
    if prestamo[1] != "ACTIVO":
        return False, "El préstamo no está activo"

    hoy = date.today().isoformat()
    if prestamo[2] != prestamo[3]:
        estado_ejemplar = "PENDIENTE_RETORNO"
    elif estado_fisico == "DANADO":
        estado_ejemplar = "BAJA"
    else:
        estado_ejemplar = "DISPONIBLE"

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
        """, (estado_ejemplar, estado_fisico, prestamo[0]))

        conexion.commit()
        return True, "Devolución registrada"
    except Exception:
        conexion.rollback()
        raise


def cancelar_solicitud_interbibliotecaria(id_prestamo, nombre_archivo=ARCHIVO_BD):
    """Cancela una solicitud interbibliotecaria que todavía no se activó
    (el socio desistió o quedó inhabilitado).

    - Si el ejemplar no salió de su sede, vuelve a quedar DISPONIBLE y el
      remito de envío que estuviera preparado ya no se puede despachar.
    - Si el ejemplar ya llegó a la sede destino, queda PENDIENTE_RETORNO
      para generar el remito de retorno.
    - Si el ejemplar está viajando, hay que esperar a que llegue.
    """
    conexion = conectar(nombre_archivo)
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT p.estado, e.estado, e.sede_actual_id,
               p.sede_origen_id, p.sede_destino_id, p.ejemplar_id
        FROM prestamos p
        JOIN ejemplares e ON e.id = p.ejemplar_id
        WHERE p.id = ?
    """, (id_prestamo,))
    fila = cursor.fetchone()
    if fila is None:
        return False, "Préstamo inexistente"
    if fila[0] != "SOLICITADO":
        return False, "Sólo se pueden cancelar solicitudes pendientes"

    if fila[1] == "RESERVADO" and fila[2] == fila[3]:
        nuevo_estado = "DISPONIBLE"
        mensaje = "Solicitud cancelada. El ejemplar vuelve a estar disponible."
    elif fila[1] == "RESERVADO" and fila[2] == fila[4]:
        nuevo_estado = "PENDIENTE_RETORNO"
        mensaje = "Solicitud cancelada. Genere el remito de retorno."
    else:
        return False, "El ejemplar está en tránsito: espere a recibirlo para cancelar"

    try:
        cursor.execute("UPDATE prestamos SET estado = 'CANCELADO' WHERE id = ?",
                       (id_prestamo,))
        cursor.execute("UPDATE ejemplares SET estado = ? WHERE id = ?",
                       (nuevo_estado, fila[5]))
        conexion.commit()
        return True, mensaje
    except Exception:
        conexion.rollback()
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
    return prestamo


def listar_prestamos_pendientes_retorno(nombre_archivo=ARCHIVO_BD):
    conexion = conectar(nombre_archivo)
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT p.id, s.nombre || ' ' || s.apellido, l.titulo,
               so.nombre, sd.nombre
        FROM prestamos p
        JOIN socios s ON s.id = p.socio_id
        JOIN ejemplares e ON e.id = p.ejemplar_id
        JOIN libros l ON l.id = e.libro_id
        JOIN sedes so ON so.id = p.sede_origen_id
        JOIN sedes sd ON sd.id = p.sede_destino_id
        WHERE p.estado IN ('DEVUELTO', 'CANCELADO')
          AND p.sede_origen_id <> p.sede_destino_id
          AND e.estado = 'PENDIENTE_RETORNO'
          AND e.sede_actual_id = p.sede_destino_id
          AND NOT EXISTS (
              SELECT 1
              FROM remitos r
              WHERE r.prestamo_id = p.id
                AND r.sede_origen_id = p.sede_destino_id
                AND r.sede_destino_id = p.sede_origen_id
          )
        ORDER BY p.id DESC
    """)
    prestamos = cursor.fetchall()
    return prestamos


def listar_prestamos(nombre_archivo=ARCHIVO_BD):
    conexion = conectar(nombre_archivo)
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT p.id, s.dni, s.nombre || ' ' || s.apellido,
               l.titulo, e.codigo, so.nombre, sd.nombre,
               p.fecha_solicitud, p.fecha_inicio, p.fecha_vencimiento,
               p.estado
        FROM prestamos p
        JOIN socios s ON s.id = p.socio_id
        JOIN ejemplares e ON e.id = p.ejemplar_id
        JOIN libros l ON l.id = e.libro_id
        JOIN sedes so ON so.id = p.sede_origen_id
        JOIN sedes sd ON sd.id = p.sede_destino_id
        ORDER BY p.id DESC
    """)
    prestamos = cursor.fetchall()
    return prestamos
