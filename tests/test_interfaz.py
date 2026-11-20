from types import SimpleNamespace
from unittest.mock import Mock, patch

from interfaz.app import BibliotecaApp


class CampoFalso:
    def __init__(self, valor):
        self.valor = valor

    def get(self):
        return self.valor

    def set(self, valor):
        self.valor = valor


def app_prestamos_falsa():
    app = SimpleNamespace(
        combo_prestamo_socio=CampoFalso("1 - Ana"),
        combo_prestamo_ejemplar=CampoFalso("2 - Ejemplar"),
        combo_prestamo_sede=CampoFalso("3 - Norte"),
        var_dias=CampoFalso("7"),
        id_combo=lambda campo: int(campo.get().split(" - ")[0]),
        mostrar_resultado=lambda *args: None,
        refrescar_todo=lambda: None,
    )
    app.limpiar_form_prestamo = lambda restablecer_dias=True: BibliotecaApp.limpiar_form_prestamo(
        app, restablecer_dias
    )
    return app


def test_prestamo_local_limpia_el_formulario_solo_si_fue_exitoso():
    app = app_prestamos_falsa()
    with patch("interfaz.app.registrar_prestamo_local", return_value=(False, "Error")):
        BibliotecaApp.crear_prestamo_local(app)
    assert app.combo_prestamo_socio.get() == "1 - Ana"
    assert app.var_dias.get() == "7"

    with patch("interfaz.app.registrar_prestamo_local", return_value=(True, 8)):
        BibliotecaApp.crear_prestamo_local(app)
    assert app.combo_prestamo_socio.get() == ""
    assert app.combo_prestamo_ejemplar.get() == ""
    assert app.combo_prestamo_sede.get() == ""
    assert app.var_dias.get() == "14"


def test_solicitud_limpia_selectores_pero_conserva_dias_para_activar():
    app = app_prestamos_falsa()
    with patch("interfaz.app.solicitar_prestamo_interbibliotecario", return_value=(True, 3)):
        BibliotecaApp.crear_prestamo_inter(app)
    assert app.combo_prestamo_socio.get() == ""
    assert app.combo_prestamo_ejemplar.get() == ""
    assert app.combo_prestamo_sede.get() == ""
    assert app.var_dias.get() == "7"


def test_activar_prestamo_interbibliotecario_usa_dias_del_formulario():
    app = app_prestamos_falsa()
    app.tree_prestamos = object()
    app.fila_seleccionada = lambda tree: (3,)
    with patch("interfaz.app.activar_prestamo_interbibliotecario", return_value=(True, "Préstamo activado")) as activar:
        BibliotecaApp.activar_inter(app)
    activar.assert_called_once_with(3, 7)
    assert app.var_dias.get() == "14"


def test_guardar_socio_limpia_formulario_solo_despues_de_guardar():
    eventos = []
    datos = {
        "dni": CampoFalso("40000002"),
        "nombre": CampoFalso("Juan"),
        "apellido": CampoFalso("Gómez"),
        "telefono": CampoFalso("3515555555"),
        "email": CampoFalso("juan@ejemplo.com"),
    }
    app = SimpleNamespace(
        socio_id=None,
        socio_vars=datos,
        refrescar_todo=lambda: eventos.append("refrescar"),
        notificar=lambda mensaje: None,
    )

    def limpiar():
        eventos.append("limpiar")
        app.socio_id = None
        for campo in datos.values():
            campo.set("")

    app.limpiar_form_socio = limpiar
    with patch("interfaz.app.agregar_socio", return_value=True), patch("interfaz.app.messagebox.showinfo"):
        BibliotecaApp.guardar_socio(app)
    assert eventos == ["refrescar", "limpiar"]
    assert all(campo.get() == "" for campo in datos.values())

    datos["dni"].set("40000002")
    datos["nombre"].set("Juan")
    datos["apellido"].set("Gómez")
    eventos.clear()
    with patch("interfaz.app.agregar_socio", return_value=False), patch("interfaz.app.messagebox.showerror"):
        BibliotecaApp.guardar_socio(app)
    assert datos["nombre"].get() == "Juan"
    assert eventos == []


def test_cambiar_tipo_reporte_no_lo_genera_automaticamente():
    tree = Mock()
    app = SimpleNamespace(
        tree_reporte=tree,
        filas_por_tree={str(tree): [("prestamo", 1)]},
        busquedas={str(tree): (None, [])},
        lbl_reporte=Mock(),
    )
    with patch("interfaz.app.prestamos_activos_y_material_en_transito") as consulta:
        BibliotecaApp.seleccionar_reporte(app)

    consulta.assert_not_called()
    tree.master.destroy.assert_called_once_with()
    assert app.tree_reporte is None
    assert not app.filas_por_tree
    assert not app.busquedas
    app.lbl_reporte.config.assert_called_once_with(
        text="Presione Generar para ver el reporte seleccionado."
    )
