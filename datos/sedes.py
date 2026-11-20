from datos.base_datos import conectar, ARCHIVO_BD


def buscar_sede_duplicada(nombre, direccion, nombre_archivo=ARCHIVO_BD):
    """Una sede se considera duplicada si coincide nombre y dirección (sin distinguir mayúsculas)."""
    conexion = conectar(nombre_archivo)
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT id, nombre, direccion, telefono, email, horario, activa
        FROM sedes
        WHERE nombre = ? COLLATE NOCASE AND direccion = ? COLLATE NOCASE
    """, (nombre.strip(), direccion.strip()))
    sede = cursor.fetchone()
    return sede


def agregar_sede(sede, nombre_archivo=ARCHIVO_BD):
    """Devuelve el id de la sede creada o None si ya existe una con el mismo nombre y dirección."""
    if buscar_sede_duplicada(sede.nombre, sede.direccion, nombre_archivo) is not None:
        return None

    conexion = conectar(nombre_archivo)
    cursor = conexion.cursor()
    cursor.execute("""
        INSERT INTO sedes (nombre, direccion, telefono, email, horario, activa)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (sede.nombre, sede.direccion, sede.telefono, sede.email,
          sede.horario, int(sede.activa)))
    sede.id = cursor.lastrowid
    conexion.commit()
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
    return sede


def modificar_sede(sede, nombre_archivo=ARCHIVO_BD):
    existente = buscar_sede_duplicada(sede.nombre, sede.direccion, nombre_archivo)
    if existente is not None and existente[0] != sede.id:
        return False

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
    return modificadas > 0


def sede_tiene_movimientos_en_curso(id_sede, nombre_archivo=ARCHIVO_BD):
    """True si la sede participa de un préstamo entre sedes sin terminar,
    de un remito sin recibir o tiene ejemplares esperando volver."""
    conexion = conectar(nombre_archivo)
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT 1 FROM prestamos
        WHERE estado IN ('SOLICITADO', 'ACTIVO')
          AND sede_origen_id <> sede_destino_id
          AND (sede_origen_id = :s OR sede_destino_id = :s)
        UNION ALL
        SELECT 1 FROM remitos
        WHERE estado IN ('DESPACHADO', 'EN_TRANSITO')
          AND (sede_origen_id = :s OR sede_destino_id = :s)
        UNION ALL
        SELECT 1 FROM ejemplares
        WHERE estado IN ('PENDIENTE_RETORNO', 'EN_TRANSITO')
          AND (sede_pertenencia_id = :s OR sede_actual_id = :s)
        LIMIT 1
    """, {"s": id_sede})
    en_curso = cursor.fetchone() is not None
    return en_curso


def cambiar_estado_sede(id_sede, activa, nombre_archivo=ARCHIVO_BD):
    """Devuelve False si la sede no existe o si se intenta dar de baja una
    sede con préstamos o traslados entre sedes en curso."""
    if not activa and sede_tiene_movimientos_en_curso(id_sede, nombre_archivo):
        return False

    conexion = conectar(nombre_archivo)
    cursor = conexion.cursor()
    cursor.execute("""
        UPDATE sedes
        SET activa = ?
        WHERE id = ?
    """, (int(activa), id_sede))
    conexion.commit()
    modificadas = cursor.rowcount
    return modificadas > 0
