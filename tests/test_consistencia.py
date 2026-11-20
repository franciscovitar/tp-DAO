"""Pruebas de lógica de negocio y consistencia de datos: que préstamos,
ejemplares, reservas y remitos no queden en estados trabados o a medias."""
import os
import sqlite3
from datetime import date, timedelta

import pytest

from datos.base_datos import crear_tablas, conectar, DatabaseSingleton
from datos.sedes import agregar_sede, cambiar_estado_sede
from datos.socios import agregar_socio, cambiar_habilitacion_socio
from datos.libros import agregar_libro
from datos.ejemplares import (agregar_ejemplar, buscar_ejemplar_por_codigo,
                              cambiar_estado_fisico_ejemplar)
from datos.prestamos import (
    listar_prestamos_pendientes_retorno,
    registrar_prestamo_local,
    solicitar_prestamo_interbibliotecario,
    activar_prestamo_interbibliotecario,
    registrar_devolucion,
    cancelar_solicitud_interbibliotecaria,
    buscar_prestamo,
)
from datos.reservas import registrar_reserva, buscar_reserva
from datos.remitos import (crear_remito, crear_remito_retorno,
                           cambiar_estado_remito, listar_historial_remito)
from datos.reportes import (movimientos_y_tiempo_promedio_transito,
                            disponibilidad_catalogo_por_sede)
from modelos.sede import Sede
from modelos.socio import Socio
from modelos.libro import Libro
from modelos.ejemplar import Ejemplar
from modelos.prestamo import Prestamo
from patrones.observer import Observer

BD = "test_consistencia.db"


def setup_function():
    if os.path.exists(BD):
        os.remove(BD)
    crear_tablas(BD)


def teardown_function():
    DatabaseSingleton(BD).close_connection()
    if os.path.exists(BD):
        os.remove(BD)


def datos():
    centro = Sede("Centro", "Colon 100", "111", "c@mail.com", "8 a 20")
    norte = Sede("Norte", "Rivadavia 200", "222", "n@mail.com", "8 a 20")
    agregar_sede(centro, BD)
    agregar_sede(norte, BD)
    ana = Socio("40111222", "Ana", "Perez", "111", "ana@mail.com")
    beto = Socio("40111333", "Beto", "Gomez", "222", "beto@mail.com")
    agregar_socio(ana, BD)
    agregar_socio(beto, BD)
    libro = Libro("9789500000001", "Uno", "Autor", "Ed", 2020)
    agregar_libro(libro, BD)
    ej = Ejemplar("EJ-001", libro, centro)
    agregar_ejemplar(ej, BD)
    return centro, norte, ana, beto, ej


def estado_ej(codigo="EJ-001"):
    return buscar_ejemplar_por_codigo(codigo, BD)[5]


def avanzar(id_remito, hasta="RECIBIDO"):
    for e in ("DESPACHADO", "EN_TRANSITO", "RECIBIDO"):
        ok, msg = cambiar_estado_remito(id_remito, e, nombre_archivo=BD)
        assert ok, msg
        if e == hasta:
            return


def ejecutar(sql, params=()):
    c = conectar(BD)
    c.execute(sql, params)
    c.commit()
    c.close()


# ---------------------------------------------------------------------------
# 1. Solicitudes interbibliotecarias que no se pueden cancelar
# ---------------------------------------------------------------------------

def test_solicitud_se_puede_cancelar_antes_de_enviar():
    """El socio desiste (o se inhabilita) antes de que salga el remito.
    No hay forma de liberar el ejemplar: queda RESERVADO para siempre."""
    centro, norte, ana, _, ej = datos()
    ok, id_p = solicitar_prestamo_interbibliotecario(ana.id, ej.id, norte.id, BD)
    assert ok
    cambiar_habilitacion_socio(ana.id, False, BD)

    ok, msg = cancelar_solicitud_interbibliotecaria(id_p, BD)
    assert ok, f"No se puede cancelar antes del envío: {msg}"
    assert buscar_prestamo(id_p, BD)[9] == "CANCELADO"
    assert estado_ej() == "DISPONIBLE"
    # Nunca salió de su sede: no necesita remito de retorno.
    assert listar_prestamos_pendientes_retorno(BD) == []


def test_remito_preparado_de_solicitud_cancelada_no_se_despacha():
    centro, norte, ana, _, ej = datos()
    _, id_p = solicitar_prestamo_interbibliotecario(ana.id, ej.id, norte.id, BD)
    _, id_r = crear_remito(id_p, "R-1", BD)
    assert cancelar_solicitud_interbibliotecaria(id_p, BD)[0]

    ok, _ = cambiar_estado_remito(id_r, "DESPACHADO", nombre_archivo=BD)
    assert not ok
    assert estado_ej() == "DISPONIBLE"
    # Ese remito muerto no impide dar de baja la sede.
    assert cambiar_estado_sede(norte.id, False, BD)


def test_no_se_cancela_con_el_ejemplar_viajando():
    centro, norte, ana, _, ej = datos()
    _, id_p = solicitar_prestamo_interbibliotecario(ana.id, ej.id, norte.id, BD)
    _, id_r = crear_remito(id_p, "R-1", BD)
    avanzar(id_r, "EN_TRANSITO")
    ok, _ = cancelar_solicitud_interbibliotecaria(id_p, BD)
    assert not ok
    assert estado_ej() == "EN_TRANSITO"
    assert buscar_prestamo(id_p, BD)[9] == "SOLICITADO"


def test_solicitud_cancelable_si_el_socio_sigue_habilitado():
    centro, norte, ana, _, ej = datos()
    _, id_p = solicitar_prestamo_interbibliotecario(ana.id, ej.id, norte.id, BD)
    _, id_r = crear_remito(id_p, "R-1", BD)
    avanzar(id_r)
    ok, msg = cancelar_solicitud_interbibliotecaria(id_p, BD)
    assert ok, f"Un socio habilitado no puede desistir: {msg}"
    assert estado_ej() == "PENDIENTE_RETORNO"
    ok, id_ret = crear_remito_retorno(id_p, "R-2", BD)
    assert ok
    avanzar(id_ret)
    assert estado_ej() == "DISPONIBLE"
    assert buscar_ejemplar_por_codigo("EJ-001", BD)[4] == centro.id


# ---------------------------------------------------------------------------
# 2. Baja de sede con movimientos en curso
# ---------------------------------------------------------------------------

def test_no_se_da_de_baja_una_sede_con_remitos_en_curso():
    centro, norte, ana, _, ej = datos()
    _, id_p = solicitar_prestamo_interbibliotecario(ana.id, ej.id, norte.id, BD)
    _, id_r = crear_remito(id_p, "R-1", BD)
    avanzar(id_r, "EN_TRANSITO")
    assert not cambiar_estado_sede(norte.id, False, BD), \
        "Se dio de baja una sede que tiene un remito en camino hacia ella"
    assert not cambiar_estado_sede(centro.id, False, BD)


def test_sede_se_puede_dar_de_baja_cuando_termina_el_circuito():
    centro, norte, ana, _, ej = datos()
    _, id_p = solicitar_prestamo_interbibliotecario(ana.id, ej.id, norte.id, BD)
    assert not cambiar_estado_sede(norte.id, False, BD)  # solicitud pendiente
    _, id_r = crear_remito(id_p, "R-1", BD)
    avanzar(id_r)
    activar_prestamo_interbibliotecario(id_p, 7, BD)
    assert not cambiar_estado_sede(norte.id, False, BD)  # préstamo activo
    registrar_devolucion(id_p, "BUENO", BD)
    assert not cambiar_estado_sede(centro.id, False, BD)  # falta el retorno
    _, id_ret = crear_remito_retorno(id_p, "R-2", BD)
    avanzar(id_ret)
    assert cambiar_estado_sede(norte.id, False, BD)
    assert cambiar_estado_sede(centro.id, False, BD)
    assert cambiar_estado_sede(centro.id, True, BD)


def test_sede_con_prestamo_local_activo_se_puede_dar_de_baja():
    centro, norte, ana, _, ej = datos()
    assert registrar_prestamo_local(ana.id, ej.id, centro.id, 7, BD)[0]
    assert cambiar_estado_sede(centro.id, False, BD)


def test_recibir_remito_en_sede_dada_de_baja():
    """Despachar controla las sedes; recibir no. El ejemplar llega a una
    sede cerrada y la solicitud queda sin salida (no se activa ni se cancela)."""
    centro, norte, ana, _, ej = datos()
    _, id_p = solicitar_prestamo_interbibliotecario(ana.id, ej.id, norte.id, BD)
    _, id_r = crear_remito(id_p, "R-1", BD)
    avanzar(id_r, "EN_TRANSITO")
    # La interfaz ya no lo permite; se fuerza en la base como defensa.
    ejecutar("UPDATE sedes SET activa = 0 WHERE id = ?", (norte.id,))

    ok, _ = cambiar_estado_remito(id_r, "RECIBIDO", nombre_archivo=BD)
    assert not ok, "Se recibió un remito en una sede dada de baja"
    assert estado_ej() == "EN_TRANSITO"


def test_ejemplar_no_queda_varado_si_cierra_la_sede_de_pertenencia():
    centro, norte, ana, _, ej = datos()
    _, id_p = solicitar_prestamo_interbibliotecario(ana.id, ej.id, norte.id, BD)
    _, id_r = crear_remito(id_p, "R-1", BD)
    avanzar(id_r)
    activar_prestamo_interbibliotecario(id_p, 7, BD)
    # No se puede cerrar la sede dueña mientras su ejemplar está afuera.
    assert not cambiar_estado_sede(centro.id, False, BD)

    ok, _ = registrar_devolucion(id_p, "BUENO", BD)
    assert ok
    assert not cambiar_estado_sede(centro.id, False, BD)
    ok, msg = crear_remito_retorno(id_p, "R-2", BD)
    assert ok, f"El ejemplar no puede volver a su sede: {msg}"


# ---------------------------------------------------------------------------
# 3. Reservas y socios inhabilitados / con vencidos
# ---------------------------------------------------------------------------

def test_inhabilitar_socio_libera_su_reserva():
    centro, norte, ana, beto, ej = datos()
    ok, id_res = registrar_reserva(ana.id, ej.id, centro.id, BD)
    assert ok
    cambiar_habilitacion_socio(ana.id, False, BD)
    # Ana ya no puede retirar el libro y nadie más puede pedirlo.
    assert buscar_reserva(id_res, BD)[5] == "CANCELADA"
    assert estado_ej() == "DISPONIBLE"
    ok, msg = registrar_prestamo_local(beto.id, ej.id, centro.id, 7, BD)
    assert ok, f"El ejemplar quedó bloqueado por la reserva de un socio inhabilitado: {msg}"


def test_inhabilitar_socio_no_toca_reservas_cumplidas_ni_ajenas():
    centro, norte, ana, beto, ej = datos()
    libro2 = Libro("9789500000002", "Dos", "Autor", "Ed", 2020)
    agregar_libro(libro2, BD)
    ej2 = Ejemplar("EJ-002", libro2, centro)
    agregar_ejemplar(ej2, BD)
    _, res_ana = registrar_reserva(ana.id, ej.id, centro.id, BD)
    registrar_prestamo_local(ana.id, ej.id, centro.id, 7, BD)  # la cumple
    _, res_beto = registrar_reserva(beto.id, ej2.id, centro.id, BD)

    cambiar_habilitacion_socio(ana.id, False, BD)
    assert buscar_reserva(res_ana, BD)[5] == "CUMPLIDA"
    assert estado_ej() == "PRESTADO"
    assert buscar_reserva(res_beto, BD)[5] == "ACTIVA"
    assert estado_ej("EJ-002") == "RESERVADO"


def test_reserva_bloqueada_si_el_socio_tiene_vencidos():
    centro, norte, ana, _, ej = datos()
    libro2 = Libro("9789500000002", "Dos", "Autor", "Ed", 2020)
    agregar_libro(libro2, BD)
    ej2 = Ejemplar("EJ-002", libro2, centro)
    agregar_ejemplar(ej2, BD)
    _, id_p = registrar_prestamo_local(ana.id, ej2.id, centro.id, 7, BD)
    ejecutar("UPDATE prestamos SET fecha_vencimiento = ? WHERE id = ?",
             ((date.today() - timedelta(days=3)).isoformat(), id_p))

    ok, _ = registrar_reserva(ana.id, ej.id, centro.id, BD)
    assert not ok, "Un socio con préstamos vencidos puede reservar (no puede pedir prestado)"


def test_activar_controla_prestamos_vencidos():
    centro, norte, ana, _, ej = datos()
    libro2 = Libro("9789500000002", "Dos", "Autor", "Ed", 2020)
    agregar_libro(libro2, BD)
    ej2 = Ejemplar("EJ-002", libro2, norte)
    agregar_ejemplar(ej2, BD)

    _, id_inter = solicitar_prestamo_interbibliotecario(ana.id, ej.id, norte.id, BD)
    _, id_local = registrar_prestamo_local(ana.id, ej2.id, norte.id, 7, BD)
    ejecutar("UPDATE prestamos SET fecha_vencimiento = ? WHERE id = ?",
             ((date.today() - timedelta(days=3)).isoformat(), id_local))
    _, id_r = crear_remito(id_inter, "R-1", BD)
    avanzar(id_r)

    ok, _ = activar_prestamo_interbibliotecario(id_inter, 7, BD)
    assert not ok, "Se activó un préstamo a un socio con préstamos vencidos"


# ---------------------------------------------------------------------------
# 4. Transacciones a medias
# ---------------------------------------------------------------------------

def test_cancelar_solicitud_no_deja_cambios_a_medias():
    """cancelar_solicitud_interbibliotecaria no tiene try/rollback. Si falla
    el segundo UPDATE, el primero queda pendiente en la conexión compartida
    y lo confirma el commit de la operación siguiente."""
    centro, norte, ana, _, ej = datos()
    _, id_p = solicitar_prestamo_interbibliotecario(ana.id, ej.id, norte.id, BD)
    _, id_r = crear_remito(id_p, "R-1", BD)
    avanzar(id_r)
    cambiar_habilitacion_socio(ana.id, False, BD)

    # Simulamos una falla en el UPDATE del ejemplar.
    ejecutar("""CREATE TRIGGER falla BEFORE UPDATE OF estado ON ejemplares
                WHEN NEW.estado = 'PENDIENTE_RETORNO'
                BEGIN SELECT RAISE(ABORT, 'falla simulada'); END""")
    with pytest.raises(sqlite3.DatabaseError):
        cancelar_solicitud_interbibliotecaria(id_p, BD)

    # Cualquier operación posterior que haga commit...
    cambiar_habilitacion_socio(ana.id, False, BD)

    assert buscar_prestamo(id_p, BD)[9] == "SOLICITADO", \
        "El préstamo quedó CANCELADO pero el ejemplar sigue RESERVADO"
    assert estado_ej() == "RESERVADO"


# ---------------------------------------------------------------------------
# 5. Observer
# ---------------------------------------------------------------------------

class Espia(Observer):
    def __init__(self):
        self.vistos = []

    def update(self, subject):
        self.vistos.append(subject.estado)


def test_observer_no_notifica_cambios_que_se_revierten():
    centro, norte, ana, _, ej = datos()
    _, id_p = solicitar_prestamo_interbibliotecario(ana.id, ej.id, norte.id, BD)
    _, id_r = crear_remito(id_p, "R-1", BD)
    ejecutar("""CREATE TRIGGER falla BEFORE UPDATE ON remitos
                BEGIN SELECT RAISE(ABORT, 'falla simulada'); END""")
    espia = Espia()
    with pytest.raises(sqlite3.DatabaseError):
        cambiar_estado_remito(id_r, "DESPACHADO", [espia], BD)

    assert espia.vistos == [], \
        "El observador fue notificado de un DESPACHADO que nunca se guardó"


def test_observer_se_notifica_una_vez_por_cambio_guardado():
    centro, norte, ana, _, ej = datos()
    _, id_p = solicitar_prestamo_interbibliotecario(ana.id, ej.id, norte.id, BD)
    _, id_r = crear_remito(id_p, "R-1", BD)
    espia = Espia()
    assert not cambiar_estado_remito(id_r, "RECIBIDO", [espia], BD)[0]  # salto inválido
    for e in ("DESPACHADO", "EN_TRANSITO", "RECIBIDO"):
        assert cambiar_estado_remito(id_r, e, [espia], BD)[0]
    assert espia.vistos == ["DESPACHADO", "EN_TRANSITO", "RECIBIDO"]
    assert [f[0] for f in listar_historial_remito(id_r, BD)] == \
        ["PREPARADO", "DESPACHADO", "EN_TRANSITO", "RECIBIDO"]


def test_historial_preparado_lo_registra_el_observer(monkeypatch):
    """El estado inicial también pasa por HistorialRemitoObserver."""
    import patrones.observer as obs
    llamadas = []
    original = obs.HistorialRemitoObserver.update

    def contar(self, subject):
        llamadas.append(subject.estado)
        original(self, subject)

    monkeypatch.setattr(obs.HistorialRemitoObserver, "update", contar)
    centro, norte, ana, _, ej = datos()
    _, id_p = solicitar_prestamo_interbibliotecario(ana.id, ej.id, norte.id, BD)
    _, id_r = crear_remito(id_p, "R-1", BD)
    assert llamadas == ["PREPARADO"]
    assert [f[0] for f in listar_historial_remito(id_r, BD)] == ["PREPARADO"]


# ---------------------------------------------------------------------------
# 6. Reportes
# ---------------------------------------------------------------------------

def test_movimientos_no_cuenta_remitos_que_no_salieron():
    centro, norte, ana, _, ej = datos()
    _, id_p = solicitar_prestamo_interbibliotecario(ana.id, ej.id, norte.id, BD)
    crear_remito(id_p, "R-1", BD)  # queda PREPARADO, nunca se despacha
    movs = movimientos_y_tiempo_promedio_transito(BD)["movimientos"]
    assert movs == [], f"Cuenta como envío un remito que no salió: {movs}"
    cambiar_estado_remito(1, "DESPACHADO", nombre_archivo=BD)
    movs = movimientos_y_tiempo_promedio_transito(BD)["movimientos"]
    assert movs == [("Centro", "Norte", 1)]


def test_disponibilidad_no_muestra_sedes_dadas_de_baja():
    centro, norte, ana, _, ej = datos()
    assert cambiar_estado_sede(centro.id, False, BD)
    filas = disponibilidad_catalogo_por_sede(BD)
    assert filas == [], f"Muestra disponibles en una sede cerrada: {filas}"
    cambiar_estado_sede(centro.id, True, BD)
    assert len(disponibilidad_catalogo_por_sede(BD)) == 1


# ---------------------------------------------------------------------------
# 7. Modelo y funciones sin control
# ---------------------------------------------------------------------------

def test_esta_vencido_con_fecha_leida_de_la_base():
    p = Prestamo(None, None, None, None, "2020-01-01", "2020-01-01", "2020-01-15")
    assert p.esta_vencido() is True
    futuro = (date.today() + timedelta(days=5)).isoformat()
    assert Prestamo(None, None, None, None, "x", "x", futuro).esta_vencido() is False
    assert Prestamo(None, None, None, None, "x", None, None,
                    estado="SOLICITADO").esta_vencido() is False


def test_estado_fisico_valida_el_valor():
    centro, norte, ana, _, ej = datos()
    assert not cambiar_estado_fisico_ejemplar(ej.id, "CUALQUIERA", BD)
    assert buscar_ejemplar_por_codigo("EJ-001", BD)[6] == "BUENO"


def test_singleton_comparte_instancia_y_reabre_la_conexion():
    """Una sola instancia administra la conexión; si una operación la cerró,
    la siguiente la vuelve a abrir sobre el mismo archivo."""
    a = DatabaseSingleton(BD)
    b = DatabaseSingleton(BD)
    assert a is b
    conexion = conectar(BD)
    conexion.close()
    assert conectar(BD).execute("SELECT COUNT(*) FROM sedes").fetchone() == (0,)
    assert a.nombre_archivo == BD
