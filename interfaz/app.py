import tkinter as tk
from datetime import datetime
from tkinter import ttk, messagebox

from interfaz.estilo import aplicar_estilo, FILA_ALTERNA
from modelos.sede import Sede
from modelos.socio import Socio
from modelos.libro import Libro
from modelos.ejemplar import Ejemplar
from datos.sedes import listar_sedes, agregar_sede, modificar_sede, cambiar_estado_sede
from datos.socios import listar_socios, agregar_socio, modificar_socio, cambiar_habilitacion_socio
from datos.libros import listar_libros, agregar_libro, modificar_libro
from datos.ejemplares import listar_ejemplares, agregar_ejemplar, cambiar_estado_ejemplar
from datos.prestamos import (
    listar_prestamos,
    listar_prestamos_pendientes_retorno,
    registrar_prestamo_local,
    solicitar_prestamo_interbibliotecario,
    activar_prestamo_interbibliotecario,
    cancelar_solicitud_interbibliotecaria,
    registrar_devolucion,
)
from datos.reservas import listar_reservas, registrar_reserva, cancelar_reserva
from datos.remitos import (
    listar_remitos,
    crear_remito,
    crear_remito_retorno,
    cambiar_estado_remito,
    listar_historial_remito,
)
from datos.validaciones import (
    MIN_DIAS_PRESTAMO,
    MAX_DIAS_PRESTAMO,
    validar_datos_sede,
    validar_datos_socio,
    validar_datos_libro,
    validar_codigo,
    validar_dias_prestamo,
)
from datos.reportes import (
    prestamos_activos_y_material_en_transito,
    libros_mas_solicitados_interbibliotecarios,
    disponibilidad_catalogo_por_sede,
    movimientos_y_tiempo_promedio_transito,
    prestamos_vencidos,
)


# Textos legibles para los estados que se guardan en mayúsculas en la base.
ESTADOS_LEGIBLES = {
    "DISPONIBLE": "Disponible",
    "PRESTADO": "Prestado",
    "RESERVADO": "Reservado",
    "EN_TRANSITO": "En tránsito",
    "BAJA": "De baja",
    "BUENO": "Bueno",
    "DANADO": "Dañado",
    "SOLICITADO": "Solicitado",
    "ACTIVO": "Activo",
    "DEVUELTO": "Devuelto",
    "VENCIDO": "Vencido",
    "CANCELADO": "Cancelado",
    "CANCELADA": "Cancelada",
    "ACTIVA": "Activa",
    "PENDIENTE": "Pendiente",
    "CUMPLIDA": "Cumplida",
    "PREPARADO": "Preparado",
    "DESPACHADO": "Despachado",
    "RECIBIDO": "Recibido",
}

ESTADO_FISICO_DEVOLUCION = {"Bueno": "BUENO", "Dañado": "DANADO"}

# Columnas que se muestran centradas; el resto (textos) se alinea a la izquierda.
COLUMNAS_CENTRADAS = {
    "id", "dni", "anio", "codigo", "numero", "prestamo", "ejemplar",
    "solicitud", "inicio", "vencimiento", "fecha", "creacion", "despacho",
    "recepcion", "cantidad", "estado", "fisico",
}

SIN_DATO = "—"


def formatear_valor(valor):
    """Convierte un valor de la base en el texto que ve el usuario."""
    if valor is None or valor == "":
        return SIN_DATO
    if isinstance(valor, str):
        if valor in ESTADOS_LEGIBLES:
            return ESTADOS_LEGIBLES[valor]
        texto = valor.replace("T", " ")
        for formato_origen, formato_destino in (
            ("%Y-%m-%d %H:%M:%S.%f", "%d/%m/%Y %H:%M"),
            ("%Y-%m-%d %H:%M:%S", "%d/%m/%Y %H:%M"),
            ("%Y-%m-%d %H:%M", "%d/%m/%Y %H:%M"),
            ("%Y-%m-%d", "%d/%m/%Y"),
        ):
            try:
                return datetime.strptime(texto, formato_origen).strftime(formato_destino)
            except ValueError:
                continue
    return valor


class BibliotecaApp(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("Biblioteca · Préstamos interbibliotecarios")
        aplicar_estilo(self)
        self.minsize(1080, 680)
        self._centrar(1240, 760)

        self.filas_por_tree = {}
        self._id_aviso = None

        # La barra de estado se empaqueta primero para que siempre quede visible.
        barra = ttk.Frame(self, style="BarraEstado.TFrame")
        barra.pack(fill="x", side="bottom")
        self.lbl_estado = ttk.Label(barra, text="Listo.", style="BarraEstado.TLabel")
        self.lbl_estado.pack(side="left")

        contenedor = ttk.Frame(self, padding=(12, 12, 12, 8))
        contenedor.pack(fill="both", expand=True)
        self.notebook = ttk.Notebook(contenedor)
        self.notebook.pack(fill="both", expand=True)

        self.crear_tab_sedes()
        self.crear_tab_socios()
        self.crear_tab_catalogo()
        self.crear_tab_prestamos()
        self.crear_tab_reservas()
        self.crear_tab_remitos()
        self.crear_tab_reportes()

        self.refrescar_todo()

    def report_callback_exception(self, tipo, valor, traza):
        # Red de seguridad: cualquier error no previsto se informa al usuario
        # en lugar de quedar sólo en la consola.
        import traceback
        traceback.print_exception(tipo, valor, traza)
        messagebox.showerror("Error inesperado", f"No se pudo completar la operación.\n\n{valor}")

    # ------------------------------------------------------------------
    # Utilidades de interfaz
    # ------------------------------------------------------------------

    def _centrar(self, ancho, alto):
        ancho = min(ancho, self.winfo_screenwidth() - 40)
        alto = min(alto, self.winfo_screenheight() - 80)
        x = max((self.winfo_screenwidth() - ancho) // 2, 0)
        y = max((self.winfo_screenheight() - alto) // 3, 0)
        self.geometry(f"{ancho}x{alto}+{x}+{y}")

    def crear_pestania(self, texto, titulo, ayuda):
        tab = ttk.Frame(self.notebook, padding=(16, 14, 16, 12))
        self.notebook.add(tab, text=texto)
        encabezado = ttk.Frame(tab)
        encabezado.pack(fill="x", pady=(0, 10))
        ttk.Label(encabezado, text=titulo, style="Titulo.TLabel").pack(anchor="w")
        ttk.Label(encabezado, text=ayuda, style="Ayuda.TLabel").pack(anchor="w", pady=(2, 0))
        return tab

    def crear_formulario(self, padre, titulo):
        form = ttk.LabelFrame(padre, text=f" {titulo} ", padding=(12, 8, 12, 12))
        form.pack(fill="x", pady=(0, 10))
        return form

    def campo(self, form, texto, widget, fila, columna, requerido=False, columnspan=1):
        etiqueta = f"{texto} *" if requerido else texto
        ttk.Label(form, text=etiqueta, style="Campo.TLabel").grid(
            row=fila * 2, column=columna, columnspan=columnspan, sticky="w", padx=(0, 12), pady=(4, 2)
        )
        widget.grid(row=fila * 2 + 1, column=columna, columnspan=columnspan, sticky="ew", padx=(0, 12))
        return widget

    def barra_botones(self, form, fila, columnas, nota=None):
        barra = ttk.Frame(form)
        barra.grid(row=fila * 2, column=0, columnspan=columnas, sticky="ew", pady=(12, 0))
        if nota:
            ttk.Label(barra, text=nota, style="Ayuda.TLabel").pack(side="left")
        return barra

    def boton(self, barra, texto, comando, primario=False, lado="right"):
        estilo = "Primario.TButton" if primario else "TButton"
        boton = ttk.Button(barra, text=texto, command=comando, style=estilo)
        boton.pack(side=lado, padx=(8, 0) if lado == "right" else (0, 8))
        return boton

    def barra_acciones(self, padre, texto):
        barra = ttk.Frame(padre)
        barra.pack(fill="x", pady=(0, 6))
        ttk.Label(barra, text=texto, style="Ayuda.TLabel").pack(side="left")
        return barra

    def crear_tree(self, padre, columnas, titulos, anchos=None):
        marco = ttk.Frame(padre)
        marco.pack(fill="both", expand=True)
        tree = ttk.Treeview(marco, columns=columnas, show="headings", height=12, selectmode="browse")
        barra_v = ttk.Scrollbar(marco, orient="vertical", command=tree.yview)
        barra_h = ttk.Scrollbar(marco, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=barra_v.set, xscrollcommand=barra_h.set)
        tree.grid(row=0, column=0, sticky="nsew")
        barra_v.grid(row=0, column=1, sticky="ns")
        barra_h.grid(row=1, column=0, sticky="ew")
        marco.rowconfigure(0, weight=1)
        marco.columnconfigure(0, weight=1)

        for i, columna in enumerate(columnas):
            centrada = columna in COLUMNAS_CENTRADAS
            tree.heading(columna, text=titulos[i], anchor="center" if centrada else "w")
            ancho = 120 if anchos is None else anchos[i]
            tree.column(columna, width=ancho, minwidth=40, anchor="center" if centrada else "w",
                        stretch=columna not in ("id",))
        tree.tag_configure("alterna", background=FILA_ALTERNA)
        self.filas_por_tree[str(tree)] = {}
        return tree

    def limpiar_tree(self, tree):
        for item in tree.get_children():
            tree.delete(item)
        self.filas_por_tree.get(str(tree), {}).clear()

    def cargar_tree(self, tree, filas):
        """Carga filas mostrando valores legibles y guarda los originales.

        Treeview convierte los valores a texto (y "0123" en 123), así que los
        datos reales se guardan aparte para usarlos al seleccionar una fila.
        """
        self.limpiar_tree(tree)
        originales = self.filas_por_tree.setdefault(str(tree), {})
        for n, fila in enumerate(filas):
            iid = tree.insert(
                "", "end",
                values=[formatear_valor(v) for v in fila],
                tags=("alterna",) if n % 2 else (),
            )
            originales[iid] = tuple(fila)

    def id_combo(self, combo):
        valor = combo.get().strip()
        if not valor:
            return None
        return int(valor.split(" - ", 1)[0])

    def fila_seleccionada(self, tree):
        seleccion = tree.selection()
        if not seleccion:
            return None
        original = self.filas_por_tree.get(str(tree), {}).get(seleccion[0])
        if original is not None:
            return original
        return tree.item(seleccion[0])["values"]

    def notificar(self, mensaje):
        """Muestra un aviso no bloqueante en la barra inferior."""
        hora = datetime.now().strftime("%H:%M")
        self.lbl_estado.config(text=f"{hora}  ·  {mensaje}")
        if self._id_aviso is not None:
            self.after_cancel(self._id_aviso)
        self._id_aviso = self.after(15000, lambda: self.lbl_estado.config(text="Listo."))

    def atajos_formulario(self, entradas, guardar, limpiar):
        for entrada in entradas:
            entrada.bind("<Return>", lambda _e: guardar())
            entrada.bind("<Escape>", lambda _e: limpiar())

    @staticmethod
    def texto(valor):
        return "" if valor is None else str(valor)

    # ------------------------------------------------------------------
    # Sedes
    # ------------------------------------------------------------------

    def crear_tab_sedes(self):
        self.tab_sedes = self.crear_pestania(
            "Sedes", "Sedes",
            "Alta y modificación de sedes. Seleccione una fila para editarla.",
        )
        form = self.crear_formulario(self.tab_sedes, "Datos de la sede")

        self.sede_id = None
        self.sede_vars = {}
        campos = [
            ("nombre", "Nombre", True, 0, 0),
            ("direccion", "Dirección", True, 0, 1),
            ("horario", "Horario", False, 0, 2),
            ("telefono", "Teléfono", False, 1, 0),
            ("email", "Email", False, 1, 1),
        ]
        entradas = []
        for clave, texto, requerido, fila, columna in campos:
            var = tk.StringVar()
            entrada = ttk.Entry(form, textvariable=var)
            self.campo(form, texto, entrada, fila, columna, requerido)
            entradas.append(entrada)
            self.sede_vars[clave] = var
        # Orden fijo de claves para cargar la fila seleccionada.
        self.sede_vars = {c: self.sede_vars[c] for c in ("nombre", "direccion", "telefono", "email", "horario")}
        for c in range(3):
            form.columnconfigure(c, weight=1, uniform="sede")

        barra = self.barra_botones(form, 2, 3, "* Campos obligatorios")
        self.boton(barra, "Guardar", self.guardar_sede, primario=True)
        self.boton(barra, "Limpiar", self.limpiar_form_sede)
        self.atajos_formulario(entradas, self.guardar_sede, self.limpiar_form_sede)

        acciones = self.barra_acciones(self.tab_sedes, "Sedes registradas")
        self.boton(acciones, "Dar de baja / reactivar", self.toggle_sede)

        self.tree_sedes = self.crear_tree(
            self.tab_sedes,
            ("id", "nombre", "direccion", "telefono", "email", "horario", "estado"),
            ("ID", "Nombre", "Dirección", "Teléfono", "Email", "Horario", "Estado"),
            (50, 160, 200, 120, 200, 110, 90),
        )
        self.tree_sedes.bind("<<TreeviewSelect>>", self.cargar_sede_seleccionada)

    def guardar_sede(self):
        ok, datos = validar_datos_sede(
            self.sede_vars["nombre"].get(),
            self.sede_vars["direccion"].get(),
            self.sede_vars["telefono"].get(),
            self.sede_vars["email"].get(),
            self.sede_vars["horario"].get(),
        )
        if not ok:
            messagebox.showerror("Sedes", datos)
            return

        sede = Sede(**datos, id=self.sede_id)
        guardada = agregar_sede(sede) if self.sede_id is None else modificar_sede(sede)
        if not guardada:
            messagebox.showerror("Sedes", "Ya existe una sede con ese nombre y dirección.")
            return
        accion = "registrada" if self.sede_id is None else "modificada"
        self.notificar(f"Sede «{sede.nombre}» {accion}.")
        self.refrescar_todo()
        self.limpiar_form_sede()

    def cargar_sede_seleccionada(self, event=None):
        fila = self.fila_seleccionada(self.tree_sedes)
        if fila is None:
            return
        self.sede_id = int(fila[0])
        valores = [fila[1], fila[2], fila[3], fila[4], fila[5]]
        for clave, valor in zip(self.sede_vars.keys(), valores):
            self.sede_vars[clave].set(self.texto(valor))

    def limpiar_form_sede(self):
        self.sede_id = None
        for var in self.sede_vars.values():
            var.set("")
        self.tree_sedes.selection_remove(self.tree_sedes.selection())

    def toggle_sede(self):
        fila = self.fila_seleccionada(self.tree_sedes)
        if fila is None:
            messagebox.showwarning("Sedes", "Seleccione una sede en la tabla.")
            return
        nuevo_estado = fila[6] != "Activa"
        cambiar_estado_sede(int(fila[0]), nuevo_estado)
        self.notificar(f"Sede «{fila[1]}» {'reactivada' if nuevo_estado else 'dada de baja'}.")
        self.refrescar_todo()

    # ------------------------------------------------------------------
    # Socios
    # ------------------------------------------------------------------

    def crear_tab_socios(self):
        self.tab_socios = self.crear_pestania(
            "Socios", "Socios",
            "Alta y modificación de socios. Un socio inhabilitado no puede pedir préstamos ni reservas.",
        )
        form = self.crear_formulario(self.tab_socios, "Datos del socio")

        self.socio_id = None
        self.socio_vars = {}
        campos = [
            ("dni", "DNI", True, 0, 0),
            ("nombre", "Nombre", True, 0, 1),
            ("apellido", "Apellido", True, 0, 2),
            ("telefono", "Teléfono", False, 1, 0),
            ("email", "Email", False, 1, 1),
        ]
        entradas = []
        for clave, texto, requerido, fila, columna in campos:
            var = tk.StringVar()
            entrada = ttk.Entry(form, textvariable=var)
            self.campo(form, texto, entrada, fila, columna, requerido)
            entradas.append(entrada)
            self.socio_vars[clave] = var
        for c in range(3):
            form.columnconfigure(c, weight=1, uniform="socio")

        barra = self.barra_botones(form, 2, 3, "* Campos obligatorios")
        self.boton(barra, "Guardar", self.guardar_socio, primario=True)
        self.boton(barra, "Limpiar", self.limpiar_form_socio)
        self.atajos_formulario(entradas, self.guardar_socio, self.limpiar_form_socio)

        acciones = self.barra_acciones(self.tab_socios, "Socios registrados")
        self.boton(acciones, "Habilitar / inhabilitar", self.toggle_socio)

        self.tree_socios = self.crear_tree(
            self.tab_socios,
            ("id", "dni", "nombre", "apellido", "telefono", "email", "estado"),
            ("ID", "DNI", "Nombre", "Apellido", "Teléfono", "Email", "Estado"),
            (50, 100, 140, 140, 120, 210, 100),
        )
        self.tree_socios.bind("<<TreeviewSelect>>", self.cargar_socio_seleccionado)

    def guardar_socio(self):
        ok, datos = validar_datos_socio(
            self.socio_vars["dni"].get(),
            self.socio_vars["nombre"].get(),
            self.socio_vars["apellido"].get(),
            self.socio_vars["telefono"].get(),
            self.socio_vars["email"].get(),
        )
        if not ok:
            messagebox.showerror("Socios", datos)
            return

        socio = Socio(**datos, id=self.socio_id)
        ok = agregar_socio(socio) if self.socio_id is None else modificar_socio(socio)
        if not ok:
            messagebox.showerror("Socios", "Ya existe un socio con ese DNI.")
            return

        self.notificar(f"Socio {socio.nombre} {socio.apellido} guardado.")
        self.refrescar_todo()
        self.limpiar_form_socio()

    def cargar_socio_seleccionado(self, event=None):
        fila = self.fila_seleccionada(self.tree_socios)
        if fila is None:
            return
        self.socio_id = int(fila[0])
        valores = [fila[1], fila[2], fila[3], fila[4], fila[5]]
        for clave, valor in zip(self.socio_vars.keys(), valores):
            self.socio_vars[clave].set(self.texto(valor))

    def limpiar_form_socio(self):
        self.socio_id = None
        for var in self.socio_vars.values():
            var.set("")
        self.tree_socios.selection_remove(self.tree_socios.selection())

    def toggle_socio(self):
        fila = self.fila_seleccionada(self.tree_socios)
        if fila is None:
            messagebox.showwarning("Socios", "Seleccione un socio en la tabla.")
            return
        nuevo_estado = fila[6] != "Habilitado"
        cambiar_habilitacion_socio(int(fila[0]), nuevo_estado)
        self.notificar(f"Socio {fila[2]} {fila[3]} {'habilitado' if nuevo_estado else 'inhabilitado'}.")
        self.refrescar_todo()

    # ------------------------------------------------------------------
    # Catálogo
    # ------------------------------------------------------------------

    def crear_tab_catalogo(self):
        self.tab_catalogo = self.crear_pestania(
            "Catálogo", "Catálogo",
            "Libros (datos bibliográficos) y sus ejemplares físicos en cada sede.",
        )
        paneles = ttk.Frame(self.tab_catalogo)
        paneles.pack(fill="both", expand=True)
        paneles.columnconfigure(0, weight=1, uniform="catalogo")
        paneles.columnconfigure(1, weight=1, uniform="catalogo")
        paneles.rowconfigure(0, weight=1)

        izquierda = ttk.Frame(paneles)
        izquierda.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        derecha = ttk.Frame(paneles)
        derecha.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        # Libros
        libro_form = self.crear_formulario(izquierda, "Libro")
        self.libro_id = None
        self.libro_vars = {}
        campos = [
            ("isbn", "ISBN", True, 0, 0, 1),
            ("anio", "Año", False, 0, 1, 1),
            ("titulo", "Título", True, 1, 0, 2),
            ("autor", "Autor", True, 2, 0, 1),
            ("editorial", "Editorial", False, 2, 1, 1),
        ]
        entradas = []
        for clave, texto, requerido, fila, columna, ancho in campos:
            var = tk.StringVar()
            entrada = ttk.Entry(libro_form, textvariable=var)
            self.campo(libro_form, texto, entrada, fila, columna, requerido, columnspan=ancho)
            entradas.append(entrada)
            self.libro_vars[clave] = var
        self.libro_vars = {c: self.libro_vars[c] for c in ("isbn", "titulo", "autor", "editorial", "anio")}
        for c in range(2):
            libro_form.columnconfigure(c, weight=1, uniform="libro")
        barra = self.barra_botones(libro_form, 3, 2, "* Obligatorio")
        self.boton(barra, "Guardar libro", self.guardar_libro, primario=True)
        self.boton(barra, "Limpiar", self.limpiar_form_libro)
        self.atajos_formulario(entradas, self.guardar_libro, self.limpiar_form_libro)

        self.barra_acciones(izquierda, "Libros del catálogo")
        self.tree_libros = self.crear_tree(
            izquierda,
            ("id", "isbn", "titulo", "autor", "editorial", "anio"),
            ("ID", "ISBN", "Título", "Autor", "Editorial", "Año"),
            (36, 125, 145, 125, 80, 48),
        )
        self.tree_libros.bind("<<TreeviewSelect>>", self.cargar_libro_seleccionado)

        # Ejemplares
        ejemplar_form = self.crear_formulario(derecha, "Ejemplar físico")
        self.var_codigo_ejemplar = tk.StringVar()
        codigo = ttk.Entry(ejemplar_form, textvariable=self.var_codigo_ejemplar)
        self.campo(ejemplar_form, "Código", codigo, 0, 0, True)
        self.combo_sede_ejemplar = ttk.Combobox(ejemplar_form, state="readonly")
        self.campo(ejemplar_form, "Sede de pertenencia", self.combo_sede_ejemplar, 0, 1, True)
        self.combo_libro_ejemplar = ttk.Combobox(ejemplar_form, state="readonly")
        self.campo(ejemplar_form, "Libro", self.combo_libro_ejemplar, 1, 0, True, columnspan=2)
        for c in range(2):
            ejemplar_form.columnconfigure(c, weight=1, uniform="ejemplar")
        barra = self.barra_botones(ejemplar_form, 2, 2)
        self.boton(barra, "Agregar ejemplar", self.guardar_ejemplar, primario=True)
        codigo.bind("<Return>", lambda _e: self.guardar_ejemplar())

        acciones = self.barra_acciones(derecha, "Ejemplares")
        self.boton(acciones, "Activar / dar de baja", self.toggle_ejemplar)
        self.tree_ejemplares = self.crear_tree(
            derecha,
            ("id", "codigo", "libro", "pertenencia", "actual", "estado", "fisico"),
            ("ID", "Código", "Libro", "Pertenece a", "Ubicación", "Estado", "Físico"),
            (36, 72, 115, 100, 95, 82, 58),
        )

    def guardar_libro(self):
        ok, datos = validar_datos_libro(
            self.libro_vars["isbn"].get(),
            self.libro_vars["titulo"].get(),
            self.libro_vars["autor"].get(),
            self.libro_vars["editorial"].get(),
            str(self.libro_vars["anio"].get()),
        )
        if not ok:
            messagebox.showerror("Libros", datos)
            return

        libro = Libro(**datos, id=self.libro_id)
        ok = agregar_libro(libro) if self.libro_id is None else modificar_libro(libro)
        if not ok:
            messagebox.showerror("Libros", "Ya existe un libro con ese ISBN.")
            return
        self.notificar(f"Libro «{libro.titulo}» guardado.")
        self.refrescar_todo()
        self.limpiar_form_libro()

    def cargar_libro_seleccionado(self, event=None):
        fila = self.fila_seleccionada(self.tree_libros)
        if fila is None:
            return
        self.libro_id = int(fila[0])
        valores = [fila[1], fila[2], fila[3], fila[4], fila[5]]
        for clave, valor in zip(self.libro_vars.keys(), valores):
            self.libro_vars[clave].set(self.texto(valor))

    def limpiar_form_libro(self):
        self.libro_id = None
        for var in self.libro_vars.values():
            var.set("")
        self.tree_libros.selection_remove(self.tree_libros.selection())

    def guardar_ejemplar(self):
        id_libro = self.id_combo(self.combo_libro_ejemplar)
        id_sede = self.id_combo(self.combo_sede_ejemplar)
        if not self.var_codigo_ejemplar.get().strip() or id_libro is None or id_sede is None:
            messagebox.showerror("Ejemplar", "Complete código, libro y sede de pertenencia.")
            return
        ok, codigo = validar_codigo(self.var_codigo_ejemplar.get(), "código de ejemplar")
        if not ok:
            messagebox.showerror("Ejemplar", codigo)
            return

        libro_fila = next((x for x in listar_libros() if x[0] == id_libro), None)
        sede_fila = next((x for x in listar_sedes() if x[0] == id_sede), None)
        if libro_fila is None or sede_fila is None:
            messagebox.showerror("Ejemplar", "No se encontraron los datos seleccionados.")
            return

        libro = Libro(libro_fila[1], libro_fila[2], libro_fila[3], libro_fila[4], libro_fila[5], id=libro_fila[0])
        sede = Sede(sede_fila[1], sede_fila[2], sede_fila[3], sede_fila[4], sede_fila[5], bool(sede_fila[6]), sede_fila[0])
        if not agregar_ejemplar(Ejemplar(codigo, libro, sede)):
            messagebox.showerror("Ejemplar", "Ya existe un ejemplar con ese código.")
            return
        self.notificar(f"Ejemplar {codigo} registrado en {sede_fila[1]}.")
        self.refrescar_todo()
        self.var_codigo_ejemplar.set("")
        self.combo_libro_ejemplar.set("")
        self.combo_sede_ejemplar.set("")

    def toggle_ejemplar(self):
        fila = self.fila_seleccionada(self.tree_ejemplares)
        if fila is None:
            messagebox.showwarning("Ejemplar", "Seleccione un ejemplar en la tabla.")
            return

        estado_actual = fila[5]
        nuevo_estado = "DISPONIBLE" if estado_actual == "BAJA" else "BAJA"

        if nuevo_estado == "DISPONIBLE" and fila[6] == "DANADO":
            messagebox.showerror(
                "Ejemplar", "No se puede activar un ejemplar dañado. Debe repararse primero."
            )
            return

        if not cambiar_estado_ejemplar(int(fila[0]), nuevo_estado):
            messagebox.showerror(
                "Ejemplar",
                "El ejemplar sólo puede activarse o darse de baja si está disponible o de baja "
                "y no está dañado.",
            )
            return

        self.notificar(f"Ejemplar {fila[1]}: {ESTADOS_LEGIBLES[nuevo_estado].lower()}.")
        self.refrescar_todo()

    # ------------------------------------------------------------------
    # Préstamos
    # ------------------------------------------------------------------

    def crear_tab_prestamos(self):
        self.tab_prestamos = self.crear_pestania(
            "Préstamos", "Préstamos",
            "Préstamo local: el ejemplar está en la sede. Interbibliotecario: se solicita a otra sede "
            "y se activa cuando llega el remito.",
        )
        form = self.crear_formulario(self.tab_prestamos, "Nuevo préstamo o solicitud")
        self.combo_prestamo_socio = ttk.Combobox(form, state="readonly")
        self.combo_prestamo_ejemplar = ttk.Combobox(form, state="readonly")
        self.combo_prestamo_sede = ttk.Combobox(form, state="readonly")
        self.var_dias = tk.StringVar(value="14")
        self.campo(form, "Socio", self.combo_prestamo_socio, 0, 0, True)
        self.campo(form, "Ejemplar", self.combo_prestamo_ejemplar, 0, 1, True)
        self.campo(form, "Sede donde se retira", self.combo_prestamo_sede, 0, 2, True)
        dias = ttk.Entry(form, textvariable=self.var_dias, width=8, justify="center")
        self.campo(form, f"Días ({MIN_DIAS_PRESTAMO} a {MAX_DIAS_PRESTAMO})", dias, 0, 3)
        form.columnconfigure(0, weight=3, uniform="prestamo")
        form.columnconfigure(1, weight=4, uniform="prestamo")
        form.columnconfigure(2, weight=3, uniform="prestamo")
        form.columnconfigure(3, weight=1, uniform="prestamo")

        barra = self.barra_botones(
            form, 1, 4, "Los días se aplican al préstamo local o al activar una solicitud recibida."
        )
        self.boton(barra, "Registrar préstamo local", self.crear_prestamo_local, primario=True)
        self.boton(barra, "Solicitar a otra sede", self.crear_prestamo_inter)

        acciones = self.barra_acciones(self.tab_prestamos, "Con el préstamo seleccionado:")
        self.boton(acciones, "Actualizar", self.refrescar_todo)
        self.boton(acciones, "Activar solicitud recibida", self.activar_inter)
        self.boton(acciones, "Cancelar solicitud", self.cancelar_inter)
        self.boton(acciones, "Registrar devolución", self.devolver_prestamo)
        self.var_estado_fisico = tk.StringVar(value="Bueno")
        ttk.Combobox(
            acciones, textvariable=self.var_estado_fisico, values=tuple(ESTADO_FISICO_DEVOLUCION),
            state="readonly", width=9,
        ).pack(side="right", padx=(8, 0))
        ttk.Label(acciones, text="Estado al devolver").pack(side="right", padx=(16, 0))

        self.tree_prestamos = self.crear_tree(
            self.tab_prestamos,
            ("id", "dni", "socio", "libro", "codigo", "origen", "destino", "solicitud", "inicio", "vencimiento", "estado"),
            ("ID", "DNI", "Socio", "Libro", "Ejemplar", "Origen", "Destino", "Solicitud", "Inicio", "Vencimiento", "Estado"),
            (45, 85, 140, 170, 75, 105, 105, 90, 90, 105, 90),
        )

    def crear_prestamo_local(self):
        ids = (
            self.id_combo(self.combo_prestamo_socio),
            self.id_combo(self.combo_prestamo_ejemplar),
            self.id_combo(self.combo_prestamo_sede),
        )
        if None in ids:
            messagebox.showerror("Préstamo", "Seleccione socio, ejemplar y sede.")
            return
        ok, dias = validar_dias_prestamo(self.var_dias.get())
        if not ok:
            messagebox.showerror("Préstamo", dias)
            return
        ok, dato = registrar_prestamo_local(ids[0], ids[1], ids[2], dias)
        self.mostrar_resultado("Préstamo local", ok, dato)
        self.refrescar_todo()
        if ok:
            self.limpiar_form_prestamo()

    def crear_prestamo_inter(self):
        ids = (
            self.id_combo(self.combo_prestamo_socio),
            self.id_combo(self.combo_prestamo_ejemplar),
            self.id_combo(self.combo_prestamo_sede),
        )
        if None in ids:
            messagebox.showerror("Préstamo", "Seleccione socio, ejemplar y sede destino.")
            return
        ok, dato = solicitar_prestamo_interbibliotecario(ids[0], ids[1], ids[2])
        self.mostrar_resultado("Solicitud interbibliotecaria", ok, dato)
        self.refrescar_todo()
        if ok:
            # Los días se eligen al activar el préstamo, después de recibir el remito.
            self.limpiar_form_prestamo(restablecer_dias=False)

    def limpiar_form_prestamo(self, restablecer_dias=True):
        self.combo_prestamo_socio.set("")
        self.combo_prestamo_ejemplar.set("")
        self.combo_prestamo_sede.set("")
        if restablecer_dias:
            self.var_dias.set("14")

    def devolver_prestamo(self):
        fila = self.fila_seleccionada(self.tree_prestamos)
        if fila is None:
            messagebox.showwarning("Préstamo", "Seleccione un préstamo en la tabla.")
            return
        estado_fisico = ESTADO_FISICO_DEVOLUCION.get(self.var_estado_fisico.get(), "BUENO")
        ok, dato = registrar_devolucion(int(fila[0]), estado_fisico)
        self.mostrar_resultado("Devolución", ok, dato)
        self.refrescar_todo()
        if ok:
            self.var_estado_fisico.set("Bueno")

    def activar_inter(self):
        fila = self.fila_seleccionada(self.tree_prestamos)
        if fila is None:
            messagebox.showwarning("Préstamo", "Seleccione una solicitud recibida en la tabla.")
            return
        ok, dias = validar_dias_prestamo(self.var_dias.get())
        if not ok:
            messagebox.showerror("Préstamo", dias)
            return
        ok, dato = activar_prestamo_interbibliotecario(int(fila[0]), dias)
        self.mostrar_resultado("Préstamo interbibliotecario", ok, dato)
        self.refrescar_todo()
        if ok:
            self.var_dias.set("14")

    def cancelar_inter(self):
        fila = self.fila_seleccionada(self.tree_prestamos)
        if fila is None:
            messagebox.showwarning("Préstamo", "Seleccione una solicitud en la tabla.")
            return
        ok, dato = cancelar_solicitud_interbibliotecaria(int(fila[0]))
        self.mostrar_resultado("Cancelar solicitud", ok, dato)
        self.refrescar_todo()

    # ------------------------------------------------------------------
    # Reservas
    # ------------------------------------------------------------------

    def crear_tab_reservas(self):
        self.tab_reservas = self.crear_pestania(
            "Reservas", "Reservas",
            "Reserve un ejemplar para un socio en una sede.",
        )
        form = self.crear_formulario(self.tab_reservas, "Nueva reserva")
        self.combo_reserva_socio = ttk.Combobox(form, state="readonly")
        self.combo_reserva_ejemplar = ttk.Combobox(form, state="readonly")
        self.combo_reserva_sede = ttk.Combobox(form, state="readonly")
        self.campo(form, "Socio", self.combo_reserva_socio, 0, 0, True)
        self.campo(form, "Ejemplar", self.combo_reserva_ejemplar, 0, 1, True)
        self.campo(form, "Sede", self.combo_reserva_sede, 0, 2, True)
        form.columnconfigure(0, weight=3, uniform="reserva")
        form.columnconfigure(1, weight=4, uniform="reserva")
        form.columnconfigure(2, weight=3, uniform="reserva")
        barra = self.barra_botones(form, 1, 3)
        self.boton(barra, "Registrar reserva", self.crear_reserva, primario=True)

        acciones = self.barra_acciones(self.tab_reservas, "Reservas registradas")
        self.boton(acciones, "Cancelar reserva seleccionada", self.cancelar_reserva_ui)

        self.tree_reservas = self.crear_tree(
            self.tab_reservas,
            ("id", "dni", "socio", "libro", "codigo", "sede", "fecha", "estado"),
            ("ID", "DNI", "Socio", "Libro", "Ejemplar", "Sede", "Fecha", "Estado"),
            (50, 90, 160, 200, 90, 140, 100, 100),
        )

    def crear_reserva(self):
        ids = (
            self.id_combo(self.combo_reserva_socio),
            self.id_combo(self.combo_reserva_ejemplar),
            self.id_combo(self.combo_reserva_sede),
        )
        if None in ids:
            messagebox.showerror("Reserva", "Seleccione socio, ejemplar y sede.")
            return
        ok, dato = registrar_reserva(ids[0], ids[1], ids[2])
        self.mostrar_resultado("Reserva", ok, dato)
        self.refrescar_todo()
        if ok:
            self.combo_reserva_socio.set("")
            self.combo_reserva_ejemplar.set("")
            self.combo_reserva_sede.set("")

    def cancelar_reserva_ui(self):
        fila = self.fila_seleccionada(self.tree_reservas)
        if fila is None:
            messagebox.showwarning("Reserva", "Seleccione una reserva en la tabla.")
            return
        if not messagebox.askyesno("Cancelar reserva", f"¿Cancelar la reserva N° {fila[0]}?"):
            return
        ok, dato = cancelar_reserva(int(fila[0]))
        self.mostrar_resultado("Reserva", ok, dato)
        self.refrescar_todo()

    # ------------------------------------------------------------------
    # Remitos
    # ------------------------------------------------------------------

    def crear_tab_remitos(self):
        self.tab_remitos = self.crear_pestania(
            "Remitos", "Remitos",
            "Ciclo de un remito: Preparado → Despachado → En tránsito → Recibido.",
        )
        formularios = ttk.Frame(self.tab_remitos)
        formularios.pack(fill="x")
        formularios.columnconfigure(0, weight=1, uniform="remitos")
        formularios.columnconfigure(1, weight=1, uniform="remitos")

        ida = ttk.LabelFrame(formularios, text=" Remito de envío ", padding=(12, 8, 12, 12))
        ida.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=(0, 10))
        self.combo_remito_prestamo = ttk.Combobox(ida, state="readonly")
        self.campo(ida, "Solicitud pendiente de envío", self.combo_remito_prestamo, 0, 0, True)
        self.var_numero_remito = tk.StringVar()
        numero = ttk.Entry(ida, textvariable=self.var_numero_remito, width=14)
        self.campo(ida, "N° de remito", numero, 0, 1, True)
        ida.columnconfigure(0, weight=1)
        barra = self.barra_botones(ida, 1, 2)
        self.boton(barra, "Crear remito", self.crear_remito_ui, primario=True)
        numero.bind("<Return>", lambda _e: self.crear_remito_ui())

        vuelta = ttk.LabelFrame(formularios, text=" Remito de retorno ", padding=(12, 8, 12, 12))
        vuelta.grid(row=0, column=1, sticky="nsew", padx=(8, 0), pady=(0, 10))
        self.combo_remito_retorno = ttk.Combobox(vuelta, state="readonly")
        self.campo(vuelta, "Préstamo devuelto", self.combo_remito_retorno, 0, 0, True)
        self.var_numero_retorno = tk.StringVar()
        numero_retorno = ttk.Entry(vuelta, textvariable=self.var_numero_retorno, width=14)
        self.campo(vuelta, "N° de remito", numero_retorno, 0, 1, True)
        vuelta.columnconfigure(0, weight=1)
        barra = self.barra_botones(vuelta, 1, 2)
        self.boton(barra, "Crear remito de retorno", self.crear_remito_retorno_ui, primario=True)
        numero_retorno.bind("<Return>", lambda _e: self.crear_remito_retorno_ui())

        acciones = self.barra_acciones(self.tab_remitos, "Con el remito seleccionado:")
        self.boton(acciones, "Ver historial", self.ver_historial)
        self.boton(acciones, "Recibir", lambda: self.avanzar_remito("RECIBIDO"))
        self.boton(acciones, "Marcar en tránsito", lambda: self.avanzar_remito("EN_TRANSITO"))
        self.boton(acciones, "Despachar", lambda: self.avanzar_remito("DESPACHADO"))

        self.tree_remitos = self.crear_tree(
            self.tab_remitos,
            ("id", "numero", "prestamo", "origen", "destino", "creacion", "despacho", "recepcion", "estado"),
            ("ID", "Número", "Préstamo", "Origen", "Destino", "Creación", "Despacho", "Recepción", "Estado"),
            (50, 90, 75, 130, 130, 135, 135, 135, 100),
        )

    def crear_remito_ui(self):
        id_prestamo = self.id_combo(self.combo_remito_prestamo)
        numero = self.var_numero_remito.get().strip()
        if id_prestamo is None or not numero:
            messagebox.showerror("Remito", "Seleccione la solicitud e ingrese un número de remito.")
            return
        ok, dato = crear_remito(id_prestamo, numero)
        self.mostrar_resultado("Remito", ok, dato)
        self.refrescar_todo()
        if ok:
            self.var_numero_remito.set("")
            self.combo_remito_prestamo.set("")

    def crear_remito_retorno_ui(self):
        id_prestamo = self.id_combo(self.combo_remito_retorno)
        numero = self.var_numero_retorno.get().strip()
        if id_prestamo is None or not numero:
            messagebox.showerror("Remito", "Seleccione un préstamo devuelto e ingrese un número de remito.")
            return
        ok, dato = crear_remito_retorno(id_prestamo, numero)
        self.mostrar_resultado("Remito de retorno", ok, dato)
        self.refrescar_todo()
        if ok:
            self.var_numero_retorno.set("")
            self.combo_remito_retorno.set("")

    def avanzar_remito(self, estado):
        fila = self.fila_seleccionada(self.tree_remitos)
        if fila is None:
            messagebox.showwarning("Remito", "Seleccione un remito en la tabla.")
            return
        ok, dato = cambiar_estado_remito(int(fila[0]), estado)
        self.mostrar_resultado("Remito", ok, dato)
        self.refrescar_todo()

    def ver_historial(self):
        fila = self.fila_seleccionada(self.tree_remitos)
        if fila is None:
            messagebox.showwarning("Remito", "Seleccione un remito en la tabla.")
            return
        historial = listar_historial_remito(int(fila[0]))
        texto = "\n".join(
            f"{formatear_valor(fecha)}   {formatear_valor(estado)}" for estado, fecha in historial
        )
        messagebox.showinfo(f"Historial del remito {fila[1]}", texto if texto else "Sin movimientos.")

    # ------------------------------------------------------------------
    # Reportes
    # ------------------------------------------------------------------

    def crear_tab_reportes(self):
        self.tab_reportes = self.crear_pestania(
            "Reportes", "Reportes",
            "Elija un reporte y presione Generar. Los datos se calculan en el momento.",
        )
        superior = ttk.Frame(self.tab_reportes)
        superior.pack(fill="x", pady=(0, 10))
        ttk.Label(superior, text="Reporte").pack(side="left", padx=(0, 8))
        self.combo_reporte = ttk.Combobox(
            superior,
            state="readonly",
            width=48,
            values=(
                "Préstamos activos y material en tránsito",
                "Libros más solicitados entre sedes",
                "Disponibilidad de catálogo por sede",
                "Movimientos y tiempo promedio de tránsito",
                "Préstamos vencidos",
            ),
        )
        self.combo_reporte.current(0)
        self.combo_reporte.pack(side="left")
        self.combo_reporte.bind("<<ComboboxSelected>>", lambda _e: self.generar_reporte())
        ttk.Button(superior, text="Generar", style="Primario.TButton",
                   command=self.generar_reporte).pack(side="left", padx=(8, 0))
        self.lbl_reporte = ttk.Label(superior, text="", style="Ayuda.TLabel")
        self.lbl_reporte.pack(side="right")

        self.frame_reporte = ttk.Frame(self.tab_reportes)
        self.frame_reporte.pack(fill="both", expand=True)
        self.tree_reporte = None

    def mostrar_reporte(self, columnas, titulos, filas, anchos=None):
        if self.tree_reporte is not None:
            self.filas_por_tree.pop(str(self.tree_reporte), None)
            self.tree_reporte.master.destroy()
        self.tree_reporte = self.crear_tree(self.frame_reporte, columnas, titulos, anchos)
        self.cargar_tree(self.tree_reporte, filas)
        if not self.lbl_reporte.cget("text"):
            cantidad = len(filas)
            self.lbl_reporte.config(text="Sin resultados." if cantidad == 0 else f"{cantidad} fila(s)")

    def generar_reporte(self):
        opcion = self.combo_reporte.current()
        self.lbl_reporte.config(text="")
        if opcion == 0:
            datos = prestamos_activos_y_material_en_transito()
            filas = []
            for p in datos["prestamos_activos"]:
                filas.append(("Préstamo", p[0], p[4], p[5], p[6], p[7], p[8]))
            for r in datos["material_en_transito"]:
                filas.append(("En tránsito", r[0], r[1], r[2], r[3], r[4], r[5]))
            self.mostrar_reporte(
                ("tipo", "id", "libro", "ejemplar", "origen", "destino", "dato"),
                ("Tipo", "ID / N°", "Libro", "Ejemplar", "Origen", "Destino", "Vencimiento / estado"),
                filas,
                (100, 80, 220, 90, 140, 140, 150),
            )
        elif opcion == 1:
            datos = libros_mas_solicitados_interbibliotecarios()
            self.mostrar_reporte(("isbn", "titulo", "cantidad"), ("ISBN", "Libro", "Solicitudes"), datos,
                                 (150, 400, 120))
        elif opcion == 2:
            datos = disponibilidad_catalogo_por_sede()
            self.mostrar_reporte(("sede", "isbn", "titulo", "cantidad"), ("Sede", "ISBN", "Libro", "Disponibles"),
                                 datos, (180, 150, 360, 110))
        elif opcion == 3:
            datos = movimientos_y_tiempo_promedio_transito()
            self.lbl_reporte.config(
                text=f"Tiempo promedio de tránsito: {datos['horas_promedio_transito']:.2f} h"
            )
            self.mostrar_reporte(("origen", "destino", "cantidad"), ("Origen", "Destino", "Envíos"),
                                 datos["movimientos"], (220, 220, 120))
        else:
            datos = prestamos_vencidos()
            self.mostrar_reporte(
                ("id", "dni", "socio", "libro", "ejemplar", "vencimiento"),
                ("ID", "DNI", "Socio", "Libro", "Ejemplar", "Vencimiento"),
                datos,
                (60, 100, 180, 240, 100, 120),
            )

    # ------------------------------------------------------------------
    # Refresco general y mensajes
    # ------------------------------------------------------------------

    def refrescar_todo(self):
        sedes = listar_sedes()
        socios = listar_socios()
        libros = listar_libros()
        ejemplares = listar_ejemplares()
        prestamos = listar_prestamos()
        reservas = listar_reservas()
        remitos = listar_remitos()

        self.cargar_tree(
            self.tree_sedes,
            [(s[0], s[1], s[2], s[3], s[4], s[5], "Activa" if s[6] else "Baja") for s in sedes],
        )
        self.cargar_tree(
            self.tree_socios,
            [(s[0], s[1], s[2], s[3], s[4], s[5], "Habilitado" if s[6] else "Inhabilitado") for s in socios],
        )
        self.cargar_tree(self.tree_libros, libros)
        self.cargar_tree(self.tree_ejemplares, ejemplares)
        self.cargar_tree(self.tree_prestamos, prestamos)
        self.cargar_tree(self.tree_reservas, reservas)
        self.cargar_tree(self.tree_remitos, remitos)

        sedes_combo = [f"{s[0]} - {s[1]}" for s in sedes if s[6]]
        socios_combo = [f"{s[0]} - {s[3]}, {s[2]} (DNI {s[1]})" for s in socios if s[6]]
        libros_combo = [f"{l[0]} - {l[2]} ({l[1]})" for l in libros]
        ejemplares_combo = [
            f"{e[0]} - {e[1]} · {e[2]} · {e[4]} [{formatear_valor(e[5])}]" for e in ejemplares
        ]

        self.combo_sede_ejemplar["values"] = sedes_combo
        self.combo_libro_ejemplar["values"] = libros_combo
        self.combo_prestamo_socio["values"] = socios_combo
        self.combo_prestamo_ejemplar["values"] = ejemplares_combo
        self.combo_prestamo_sede["values"] = sedes_combo
        self.combo_reserva_socio["values"] = socios_combo
        self.combo_reserva_ejemplar["values"] = ejemplares_combo
        self.combo_reserva_sede["values"] = sedes_combo

        solicitudes = [p for p in prestamos if p[-1] == "SOLICITADO"]
        self.combo_remito_prestamo["values"] = [
            f"{p[0]} - {p[2]} · {p[3]} · {p[5]} → {p[6]}" for p in solicitudes
        ]

        devoluciones_inter = listar_prestamos_pendientes_retorno()
        self.combo_remito_retorno["values"] = [
            f"{p[0]} - {p[1]} · {p[2]} · {p[4]} → {p[3]}"
            for p in devoluciones_inter
        ]

    def mostrar_resultado(self, titulo, ok, dato):
        if ok:
            mensaje = f"{titulo} registrado correctamente (N° {dato})." if isinstance(dato, int) else str(dato)
            if titulo == "Solicitud interbibliotecaria":
                mensaje += " Los días se confirman al activarlo, cuando llegue el remito."
            self.notificar(mensaje)
        else:
            messagebox.showerror(titulo, str(dato))
