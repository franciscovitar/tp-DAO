from datos.base_datos import conectar, ARCHIVO_BD


def buscar_ejemplar_por_codigo(codigo, nombre_archivo=ARCHIVO_BD):
    conexion = conectar(nombre_archivo)
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT id, codigo, libro_id, sede_pertenencia_id, sede_actual_id,
               estado, estado_fisico
        FROM ejemplares
        WHERE codigo = ? COLLATE NOCASE
    """, (codigo,))
    ejemplar = cursor.fetchone()
    return ejemplar


def agregar_ejemplar(ejemplar, nombre_archivo=ARCHIVO_BD):
    if buscar_ejemplar_por_codigo(ejemplar.codigo, nombre_archivo) is not None:
        return False

    conexion = conectar(nombre_archivo)
    cursor = conexion.cursor()
    cursor.execute("""
        INSERT INTO ejemplares (
            codigo, libro_id, sede_pertenencia_id, sede_actual_id,
            estado, estado_fisico
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (ejemplar.codigo, ejemplar.libro.id, ejemplar.sede_pertenencia.id,
          ejemplar.sede_actual.id, ejemplar.estado, ejemplar.estado_fisico))
    ejemplar.id = cursor.lastrowid
    conexion.commit()
    return True


def listar_ejemplares(nombre_archivo=ARCHIVO_BD):
    conexion = conectar(nombre_archivo)
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT e.id, e.codigo, l.titulo, sp.nombre, sa.nombre,
               e.estado, e.estado_fisico
        FROM ejemplares e
        JOIN libros l ON l.id = e.libro_id
        JOIN sedes sp ON sp.id = e.sede_pertenencia_id
        JOIN sedes sa ON sa.id = e.sede_actual_id
        ORDER BY l.titulo, e.codigo
    """)
    ejemplares = cursor.fetchall()
    return ejemplares


def cambiar_estado_ejemplar(id_ejemplar, estado, nombre_archivo=ARCHIVO_BD):
    if estado not in ("DISPONIBLE", "BAJA"):
        return False

    conexion = conectar(nombre_archivo)
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT estado, estado_fisico
        FROM ejemplares
        WHERE id = ?
    """, (id_ejemplar,))
    ejemplar = cursor.fetchone()

    if ejemplar is None or ejemplar[0] not in ("DISPONIBLE", "BAJA"):
        return False

    # Un ejemplar dañado debe repararse antes de volver a circular.
    if estado == "DISPONIBLE" and ejemplar[1] == "DANADO":
        return False

    cursor.execute("""
        UPDATE ejemplares
        SET estado = ?
        WHERE id = ?
    """, (estado, id_ejemplar))
    conexion.commit()
    modificadas = cursor.rowcount
    return modificadas > 0


def cambiar_estado_fisico_ejemplar(id_ejemplar, estado_fisico, nombre_archivo=ARCHIVO_BD):
    if estado_fisico not in ("BUENO", "DANADO"):
        return False
    conexion = conectar(nombre_archivo)
    cursor = conexion.cursor()
    cursor.execute("""
        UPDATE ejemplares
        SET estado_fisico = ?
        WHERE id = ?
    """, (estado_fisico, id_ejemplar))
    conexion.commit()
    modificadas = cursor.rowcount
    return modificadas > 0


def marcar_ejemplar_reparado(id_ejemplar, nombre_archivo=ARCHIVO_BD):
    """Un ejemplar dañado y de baja vuelve a estar disponible tras repararlo."""
    conexion = conectar(nombre_archivo)
    cursor = conexion.cursor()
    cursor.execute("""
        UPDATE ejemplares
        SET estado_fisico = 'BUENO', estado = 'DISPONIBLE'
        WHERE id = ? AND estado = 'BAJA' AND estado_fisico = 'DANADO'
    """, (id_ejemplar,))
    conexion.commit()
    modificadas = cursor.rowcount
    return modificadas > 0


def modificar_ejemplar(id_ejemplar, codigo, id_libro, id_sede, nombre_archivo=ARCHIVO_BD):
    """Modifica código, libro y sede de un ejemplar que está en su sede y sin movimientos en curso."""
    conexion = conectar(nombre_archivo)
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT estado, libro_id, sede_pertenencia_id, sede_actual_id
        FROM ejemplares WHERE id = ?
    """, (id_ejemplar,))
    ejemplar = cursor.fetchone()
    if ejemplar is None:
        return False, "Ejemplar inexistente"
    if ejemplar[0] not in ("DISPONIBLE", "BAJA") or ejemplar[2] != ejemplar[3]:
        return False, "Sólo se puede modificar un ejemplar disponible o de baja que esté en su sede"

    cursor.execute("SELECT id FROM ejemplares WHERE codigo = ? COLLATE NOCASE AND id <> ?",
                   (codigo, id_ejemplar))
    if cursor.fetchone() is not None:
        return False, "Ya existe un ejemplar con ese código"

    cursor.execute("SELECT activa FROM sedes WHERE id = ?", (id_sede,))
    sede = cursor.fetchone()
    if sede is None or sede[0] == 0:
        return False, "La sede está dada de baja"

    if id_libro != ejemplar[1]:
        cursor.execute("""
            SELECT 1 FROM prestamos WHERE ejemplar_id = ?
            UNION SELECT 1 FROM reservas WHERE ejemplar_id = ?
        """, (id_ejemplar, id_ejemplar))
        if cursor.fetchone() is not None:
            return False, "No se puede cambiar el libro de un ejemplar que ya tiene préstamos o reservas"

    cursor.execute("""
        UPDATE ejemplares
        SET codigo = ?, libro_id = ?, sede_pertenencia_id = ?, sede_actual_id = ?
        WHERE id = ?
    """, (codigo, id_libro, id_sede, id_sede, id_ejemplar))
    conexion.commit()
    return True, "Ejemplar modificado"
