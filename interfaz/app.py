import tkinter as tk
from tkinter import ttk, messagebox

from modelos.sede import Sede
from modelos.socio import Socio
from modelos.libro import Libro
from modelos.ejemplar import Ejemplar
from datos.sedes import listar_sedes, agregar_sede, modificar_sede, cambiar_estado_sede
from datos.socios import listar_socios, agregar_socio, modificar_socio, cambiar_habilitacion_socio
from datos.libros import listar_libros, agregar_libro, modificar_libro
from datos.ejemplares import listar_ejemplares, agregar_ejemplar
from datos.prestamos import (
    listar_prestamos,
    registrar_prestamo_local,
    solicitar_prestamo_interbibliotecario,
    activar_prestamo_interbibliotecario,
    registrar_devolucion,
)
from datos.reservas import listar_reservas, registrar_reserva, cancelar_reserva
from datos.remitos import listar_remitos, crear_remito, cambiar_estado_remito, listar_historial_remito
from datos.reportes import (
    prestamos_activos_y_material_en_transito,
    libros_mas_solicitados_interbibliotecarios,
    disponibilidad_catalogo_por_sede,
    movimientos_y_tiempo_promedio_transito,
)


class BibliotecaApp(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("Biblioteca - Préstamos Interbibliotecarios")
        self.geometry("1180x720")
        self.minsize(1000, 650)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.crear_tab_sedes()
        self.crear_tab_socios()
        self.crear_tab_catalogo()
        self.crear_tab_prestamos()
        self.crear_tab_reservas()
        self.crear_tab_remitos()
        self.crear_tab_reportes()

        self.refrescar_todo()

    def crear_tree(self, padre, columnas, titulos, anchos=None):
        tree = ttk.Treeview(padre, columns=columnas, show="headings", height=14)
        for i, columna in enumerate(columnas):
            tree.heading(columna, text=titulos[i])
            ancho = 120 if anchos is None else anchos[i]
            tree.column(columna, width=ancho, anchor="center")
        tree.pack(fill="both", expand=True, padx=8, pady=8)
        return tree

    def limpiar_tree(self, tree):
        for item in tree.get_children():
            tree.delete(item)

    def id_combo(self, combo):
        valor = combo.get().strip()
        if not valor:
            return None
        return int(valor.split(" - ", 1)[0])

    def fila_seleccionada(self, tree):
        seleccion = tree.selection()
        if not seleccion:
            return None
        return tree.item(seleccion[0])["values"]

    def crear_tab_sedes(self):
        self.tab_sedes = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_sedes, text="Sedes")

        form = ttk.LabelFrame(self.tab_sedes, text="Datos de la sede")
        form.pack(fill="x", padx=8, pady=8)

        self.sede_id = None
        self.sede_vars = {}
        campos = ["Nombre", "Dirección", "Teléfono", "Email", "Horario"]
        claves = ["nombre", "direccion", "telefono", "email", "horario"]
        for i, (texto, clave) in enumerate(zip(campos, claves)):
            ttk.Label(form, text=texto).grid(row=0, column=i, padx=4, pady=4, sticky="w")
            var = tk.StringVar()
            self.sede_vars[clave] = var
            ttk.Entry(form, textvariable=var, width=21).grid(row=1, column=i, padx=4, pady=4)

        ttk.Button(form, text="Guardar", command=self.guardar_sede).grid(row=1, column=5, padx=5)
        ttk.Button(form, text="Nuevo", command=self.limpiar_form_sede).grid(row=1, column=6, padx=5)
        ttk.Button(form, text="Cambiar activo/baja", command=self.toggle_sede).grid(row=1, column=7, padx=5)

        self.tree_sedes = self.crear_tree(
            self.tab_sedes,
            ("id", "nombre", "direccion", "telefono", "email", "horario", "estado"),
            ("ID", "Nombre", "Dirección", "Teléfono", "Email", "Horario", "Estado"),
            (50, 150, 180, 110, 190, 120, 80),
        )
        self.tree_sedes.bind("<<TreeviewSelect>>", self.cargar_sede_seleccionada)

    def guardar_sede(self):
        nombre = self.sede_vars["nombre"].get().strip()
        direccion = self.sede_vars["direccion"].get().strip()
        if not nombre or not direccion:
            messagebox.showerror("Datos incompletos", "Nombre y dirección son obligatorios.")
            return

        sede = Sede(
            nombre,
            direccion,
            self.sede_vars["telefono"].get().strip(),
            self.sede_vars["email"].get().strip(),
            self.sede_vars["horario"].get().strip(),
            id=self.sede_id,
        )
        if self.sede_id is None:
            agregar_sede(sede)
            messagebox.showinfo("Sedes", "Sede registrada.")
        else:
            modificar_sede(sede)
            messagebox.showinfo("Sedes", "Sede modificada.")
        self.limpiar_form_sede()
        self.refrescar_todo()

    def cargar_sede_seleccionada(self, event=None):
        fila = self.fila_seleccionada(self.tree_sedes)
        if fila is None:
            return
        self.sede_id = int(fila[0])
        valores = [fila[1], fila[2], fila[3], fila[4], fila[5]]
        for clave, valor in zip(self.sede_vars.keys(), valores):
            self.sede_vars[clave].set(valor)

    def limpiar_form_sede(self):
        self.sede_id = None
        for var in self.sede_vars.values():
            var.set("")
        self.tree_sedes.selection_remove(self.tree_sedes.selection())

    def toggle_sede(self):
        fila = self.fila_seleccionada(self.tree_sedes)
        if fila is None:
            messagebox.showwarning("Sedes", "Seleccione una sede.")
            return
        nuevo_estado = fila[6] != "Activa"
        cambiar_estado_sede(int(fila[0]), nuevo_estado)
        self.refrescar_todo()

    def crear_tab_socios(self):
        self.tab_socios = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_socios, text="Socios")

        form = ttk.LabelFrame(self.tab_socios, text="Datos del socio")
        form.pack(fill="x", padx=8, pady=8)

        self.socio_id = None
        self.socio_vars = {}
        campos = ["DNI", "Nombre", "Apellido", "Teléfono", "Email"]
        claves = ["dni", "nombre", "apellido", "telefono", "email"]
        for i, (texto, clave) in enumerate(zip(campos, claves)):
            ttk.Label(form, text=texto).grid(row=0, column=i, padx=4, pady=4, sticky="w")
            var = tk.StringVar()
            self.socio_vars[clave] = var
            ttk.Entry(form, textvariable=var, width=21).grid(row=1, column=i, padx=4, pady=4)

        ttk.Button(form, text="Guardar", command=self.guardar_socio).grid(row=1, column=5, padx=5)
        ttk.Button(form, text="Nuevo", command=self.limpiar_form_socio).grid(row=1, column=6, padx=5)
        ttk.Button(form, text="Habilitar/Inhabilitar", command=self.toggle_socio).grid(row=1, column=7, padx=5)

        self.tree_socios = self.crear_tree(
            self.tab_socios,
            ("id", "dni", "nombre", "apellido", "telefono", "email", "estado"),
            ("ID", "DNI", "Nombre", "Apellido", "Teléfono", "Email", "Estado"),
            (50, 100, 130, 130, 110, 190, 90),
        )
        self.tree_socios.bind("<<TreeviewSelect>>", self.cargar_socio_seleccionado)

    def guardar_socio(self):
        dni = self.socio_vars["dni"].get().strip()
        nombre = self.socio_vars["nombre"].get().strip()
        apellido = self.socio_vars["apellido"].get().strip()
        if not dni or not nombre or not apellido:
            messagebox.showerror("Datos incompletos", "DNI, nombre y apellido son obligatorios.")
            return
        if not dni.isdigit():
            messagebox.showerror("DNI", "El DNI debe contener solamente números.")
            return

        socio = Socio(
            dni,
            nombre,
            apellido,
            self.socio_vars["telefono"].get().strip(),
            self.socio_vars["email"].get().strip(),
            id=self.socio_id,
        )
        ok = agregar_socio(socio) if self.socio_id is None else modificar_socio(socio)
        if not ok:
            messagebox.showerror("Socios", "Ya existe un socio con ese DNI.")
            return

        messagebox.showinfo("Socios", "Datos guardados.")
        self.limpiar_form_socio()
        self.refrescar_todo()

    def cargar_socio_seleccionado(self, event=None):
        fila = self.fila_seleccionada(self.tree_socios)
        if fila is None:
            return
        self.socio_id = int(fila[0])
        valores = [fila[1], fila[2], fila[3], fila[4], fila[5]]
        for clave, valor in zip(self.socio_vars.keys(), valores):
            self.socio_vars[clave].set(valor)

    def limpiar_form_socio(self):
        self.socio_id = None
        for var in self.socio_vars.values():
            var.set("")
        self.tree_socios.selection_remove(self.tree_socios.selection())

    def toggle_socio(self):
        fila = self.fila_seleccionada(self.tree_socios)
        if fila is None:
            messagebox.showwarning("Socios", "Seleccione un socio.")
            return
        nuevo_estado = fila[6] != "Habilitado"
        cambiar_habilitacion_socio(int(fila[0]), nuevo_estado)
        self.refrescar_todo()

    def crear_tab_catalogo(self):
        self.tab_catalogo = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_catalogo, text="Catálogo")

        libro_form = ttk.LabelFrame(self.tab_catalogo, text="Libro")
        libro_form.pack(fill="x", padx=8, pady=6)
        self.libro_id = None
        self.libro_vars = {}
        campos = ["ISBN", "Título", "Autor", "Editorial", "Año"]
        claves = ["isbn", "titulo", "autor", "editorial", "anio"]
        for i, (texto, clave) in enumerate(zip(campos, claves)):
            ttk.Label(libro_form, text=texto).grid(row=0, column=i, padx=4, pady=3, sticky="w")
            var = tk.StringVar()
            self.libro_vars[clave] = var
            ttk.Entry(libro_form, textvariable=var, width=21).grid(row=1, column=i, padx=4, pady=3)
        ttk.Button(libro_form, text="Guardar libro", command=self.guardar_libro).grid(row=1, column=5, padx=5)
        ttk.Button(libro_form, text="Nuevo", command=self.limpiar_form_libro).grid(row=1, column=6, padx=5)

        self.tree_libros = self.crear_tree(
            self.tab_catalogo,
            ("id", "isbn", "titulo", "autor", "editorial", "anio"),
            ("ID", "ISBN", "Título", "Autor", "Editorial", "Año"),
            (50, 130, 220, 170, 150, 70),
        )
        self.tree_libros.configure(height=7)
        self.tree_libros.bind("<<TreeviewSelect>>", self.cargar_libro_seleccionado)

        ejemplar_form = ttk.LabelFrame(self.tab_catalogo, text="Ejemplar físico")
        ejemplar_form.pack(fill="x", padx=8, pady=6)
        ttk.Label(ejemplar_form, text="Código").grid(row=0, column=0, padx=4, pady=3)
        ttk.Label(ejemplar_form, text="Libro").grid(row=0, column=1, padx=4, pady=3)
        ttk.Label(ejemplar_form, text="Sede de pertenencia").grid(row=0, column=2, padx=4, pady=3)
        self.var_codigo_ejemplar = tk.StringVar()
        ttk.Entry(ejemplar_form, textvariable=self.var_codigo_ejemplar, width=20).grid(row=1, column=0, padx=4, pady=3)
        self.combo_libro_ejemplar = ttk.Combobox(ejemplar_form, state="readonly", width=42)
        self.combo_libro_ejemplar.grid(row=1, column=1, padx=4, pady=3)
        self.combo_sede_ejemplar = ttk.Combobox(ejemplar_form, state="readonly", width=34)
        self.combo_sede_ejemplar.grid(row=1, column=2, padx=4, pady=3)
        ttk.Button(ejemplar_form, text="Agregar ejemplar", command=self.guardar_ejemplar).grid(row=1, column=3, padx=5)

        self.tree_ejemplares = self.crear_tree(
            self.tab_catalogo,
            ("id", "codigo", "libro", "pertenencia", "actual", "estado", "fisico"),
            ("ID", "Código", "Libro", "Sede pertenencia", "Sede actual", "Estado", "Estado físico"),
            (50, 90, 220, 150, 150, 100, 100),
        )
        self.tree_ejemplares.configure(height=7)

    def guardar_libro(self):
        isbn = self.libro_vars["isbn"].get().strip()
        titulo = self.libro_vars["titulo"].get().strip()
        autor = self.libro_vars["autor"].get().strip()
        if not isbn or not titulo or not autor:
            messagebox.showerror("Datos incompletos", "ISBN, título y autor son obligatorios.")
            return

        anio_texto = self.libro_vars["anio"].get().strip()
        if anio_texto and not anio_texto.isdigit():
            messagebox.showerror("Año", "El año debe ser numérico.")
            return
        anio = int(anio_texto) if anio_texto else None
        libro = Libro(
            isbn,
            titulo,
            autor,
            self.libro_vars["editorial"].get().strip(),
            anio,
            id=self.libro_id,
        )
        ok = agregar_libro(libro) if self.libro_id is None else modificar_libro(libro)
        if not ok:
            messagebox.showerror("Libros", "Ya existe un libro con ese ISBN.")
            return
        messagebox.showinfo("Libros", "Datos guardados.")
        self.limpiar_form_libro()
        self.refrescar_todo()

    def cargar_libro_seleccionado(self, event=None):
        fila = self.fila_seleccionada(self.tree_libros)
        if fila is None:
            return
        self.libro_id = int(fila[0])
        valores = [fila[1], fila[2], fila[3], fila[4], fila[5]]
        for clave, valor in zip(self.libro_vars.keys(), valores):
            self.libro_vars[clave].set("" if valor is None else valor)

    def limpiar_form_libro(self):
        self.libro_id = None
        for var in self.libro_vars.values():
            var.set("")
        self.tree_libros.selection_remove(self.tree_libros.selection())

    def guardar_ejemplar(self):
        codigo = self.var_codigo_ejemplar.get().strip()
        id_libro = self.id_combo(self.combo_libro_ejemplar)
        id_sede = self.id_combo(self.combo_sede_ejemplar)
        if not codigo or id_libro is None or id_sede is None:
            messagebox.showerror("Ejemplar", "Complete código, libro y sede.")
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
        self.var_codigo_ejemplar.set("")
        messagebox.showinfo("Ejemplar", "Ejemplar registrado.")
        self.refrescar_todo()

    def crear_tab_prestamos(self):
        self.tab_prestamos = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_prestamos, text="Préstamos")

        form = ttk.LabelFrame(self.tab_prestamos, text="Nuevo préstamo / solicitud")
        form.pack(fill="x", padx=8, pady=8)
        self.combo_prestamo_socio = ttk.Combobox(form, state="readonly", width=28)
        self.combo_prestamo_ejemplar = ttk.Combobox(form, state="readonly", width=34)
        self.combo_prestamo_sede = ttk.Combobox(form, state="readonly", width=28)
        self.var_dias = tk.StringVar(value="14")
        for i, texto in enumerate(("Socio", "Ejemplar", "Sede local/destino", "Días")):
            ttk.Label(form, text=texto).grid(row=0, column=i, padx=4, pady=3)
        self.combo_prestamo_socio.grid(row=1, column=0, padx=4, pady=3)
        self.combo_prestamo_ejemplar.grid(row=1, column=1, padx=4, pady=3)
        self.combo_prestamo_sede.grid(row=1, column=2, padx=4, pady=3)
        ttk.Entry(form, textvariable=self.var_dias, width=8).grid(row=1, column=3, padx=4, pady=3)
        ttk.Button(form, text="Préstamo local", command=self.crear_prestamo_local).grid(row=1, column=4, padx=4)
        ttk.Button(form, text="Solicitar interbibliotecario", command=self.crear_prestamo_inter).grid(row=1, column=5, padx=4)

        acciones = ttk.Frame(self.tab_prestamos)
        acciones.pack(fill="x", padx=8)
        self.var_estado_fisico = tk.StringVar(value="BUENO")
        ttk.Label(acciones, text="Estado al devolver:").pack(side="left", padx=4)
        ttk.Combobox(acciones, textvariable=self.var_estado_fisico, values=("BUENO", "DANADO"), state="readonly", width=12).pack(side="left", padx=4)
        ttk.Button(acciones, text="Registrar devolución", command=self.devolver_prestamo).pack(side="left", padx=4)
        ttk.Button(acciones, text="Activar préstamo recibido", command=self.activar_inter).pack(side="left", padx=4)
        ttk.Button(acciones, text="Actualizar", command=self.refrescar_todo).pack(side="right", padx=4)

        self.tree_prestamos = self.crear_tree(
            self.tab_prestamos,
            ("id", "dni", "socio", "libro", "codigo", "origen", "destino", "solicitud", "inicio", "vencimiento", "estado"),
            ("ID", "DNI", "Socio", "Libro", "Ejemplar", "Origen", "Destino", "Solicitud", "Inicio", "Vencimiento", "Estado"),
            (45, 85, 130, 170, 80, 100, 100, 90, 90, 90, 90),
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
        if not self.var_dias.get().isdigit() or int(self.var_dias.get()) <= 0:
            messagebox.showerror("Préstamo", "Los días deben ser un número mayor a cero.")
            return
        ok, dato = registrar_prestamo_local(ids[0], ids[1], ids[2], int(self.var_dias.get()))
        self.mostrar_resultado("Préstamo local", ok, dato)
        self.refrescar_todo()

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

    def devolver_prestamo(self):
        fila = self.fila_seleccionada(self.tree_prestamos)
        if fila is None:
            messagebox.showwarning("Préstamo", "Seleccione un préstamo.")
            return
        ok, dato = registrar_devolucion(int(fila[0]), self.var_estado_fisico.get())
        self.mostrar_resultado("Devolución", ok, dato)
        self.refrescar_todo()

    def activar_inter(self):
        fila = self.fila_seleccionada(self.tree_prestamos)
        if fila is None:
            messagebox.showwarning("Préstamo", "Seleccione una solicitud recibida.")
            return
        ok, dato = activar_prestamo_interbibliotecario(int(fila[0]))
        self.mostrar_resultado("Préstamo interbibliotecario", ok, dato)
        self.refrescar_todo()

    def crear_tab_reservas(self):
        self.tab_reservas = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_reservas, text="Reservas")
        form = ttk.LabelFrame(self.tab_reservas, text="Nueva reserva")
        form.pack(fill="x", padx=8, pady=8)
        self.combo_reserva_socio = ttk.Combobox(form, state="readonly", width=28)
        self.combo_reserva_ejemplar = ttk.Combobox(form, state="readonly", width=34)
        self.combo_reserva_sede = ttk.Combobox(form, state="readonly", width=28)
        for i, texto in enumerate(("Socio", "Ejemplar", "Sede")):
            ttk.Label(form, text=texto).grid(row=0, column=i, padx=4, pady=3)
        self.combo_reserva_socio.grid(row=1, column=0, padx=4, pady=3)
        self.combo_reserva_ejemplar.grid(row=1, column=1, padx=4, pady=3)
        self.combo_reserva_sede.grid(row=1, column=2, padx=4, pady=3)
        ttk.Button(form, text="Registrar reserva", command=self.crear_reserva).grid(row=1, column=3, padx=5)
        ttk.Button(form, text="Cancelar seleccionada", command=self.cancelar_reserva_ui).grid(row=1, column=4, padx=5)

        self.tree_reservas = self.crear_tree(
            self.tab_reservas,
            ("id", "dni", "socio", "libro", "codigo", "sede", "fecha", "estado"),
            ("ID", "DNI", "Socio", "Libro", "Ejemplar", "Sede", "Fecha", "Estado"),
            (50, 90, 150, 190, 90, 130, 100, 100),
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

    def cancelar_reserva_ui(self):
        fila = self.fila_seleccionada(self.tree_reservas)
        if fila is None:
            messagebox.showwarning("Reserva", "Seleccione una reserva.")
            return
        ok, dato = cancelar_reserva(int(fila[0]))
        self.mostrar_resultado("Reserva", ok, dato)
        self.refrescar_todo()

    def crear_tab_remitos(self):
        self.tab_remitos = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_remitos, text="Remitos")
        form = ttk.LabelFrame(self.tab_remitos, text="Preparar remito")
        form.pack(fill="x", padx=8, pady=8)
        ttk.Label(form, text="Solicitud").grid(row=0, column=0, padx=4, pady=3)
        ttk.Label(form, text="Número de remito").grid(row=0, column=1, padx=4, pady=3)
        self.combo_remito_prestamo = ttk.Combobox(form, state="readonly", width=55)
        self.combo_remito_prestamo.grid(row=1, column=0, padx=4, pady=3)
        self.var_numero_remito = tk.StringVar()
        ttk.Entry(form, textvariable=self.var_numero_remito, width=22).grid(row=1, column=1, padx=4, pady=3)
        ttk.Button(form, text="Crear remito", command=self.crear_remito_ui).grid(row=1, column=2, padx=4)

        acciones = ttk.Frame(self.tab_remitos)
        acciones.pack(fill="x", padx=8)
        ttk.Button(acciones, text="Despachar", command=lambda: self.avanzar_remito("DESPACHADO")).pack(side="left", padx=4)
        ttk.Button(acciones, text="Marcar en tránsito", command=lambda: self.avanzar_remito("EN_TRANSITO")).pack(side="left", padx=4)
        ttk.Button(acciones, text="Recibir", command=lambda: self.avanzar_remito("RECIBIDO")).pack(side="left", padx=4)
        ttk.Button(acciones, text="Ver historial", command=self.ver_historial).pack(side="left", padx=4)

        self.tree_remitos = self.crear_tree(
            self.tab_remitos,
            ("id", "numero", "prestamo", "origen", "destino", "creacion", "despacho", "recepcion", "estado"),
            ("ID", "Número", "Préstamo", "Origen", "Destino", "Creación", "Despacho", "Recepción", "Estado"),
            (50, 90, 70, 120, 120, 150, 150, 150, 100),
        )

    def crear_remito_ui(self):
        id_prestamo = self.id_combo(self.combo_remito_prestamo)
        numero = self.var_numero_remito.get().strip()
        if id_prestamo is None or not numero:
            messagebox.showerror("Remito", "Seleccione la solicitud e ingrese un número.")
            return
        ok, dato = crear_remito(id_prestamo, numero)
        self.mostrar_resultado("Remito", ok, dato)
        if ok:
            self.var_numero_remito.set("")
        self.refrescar_todo()

    def avanzar_remito(self, estado):
        fila = self.fila_seleccionada(self.tree_remitos)
        if fila is None:
            messagebox.showwarning("Remito", "Seleccione un remito.")
            return
        ok, dato = cambiar_estado_remito(int(fila[0]), estado)
        self.mostrar_resultado("Remito", ok, dato)
        self.refrescar_todo()

    def ver_historial(self):
        fila = self.fila_seleccionada(self.tree_remitos)
        if fila is None:
            messagebox.showwarning("Remito", "Seleccione un remito.")
            return
        historial = listar_historial_remito(int(fila[0]))
        texto = "\n".join(f"{estado} - {fecha}" for estado, fecha in historial)
        messagebox.showinfo(f"Historial {fila[1]}", texto if texto else "Sin movimientos.")

    def crear_tab_reportes(self):
        self.tab_reportes = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_reportes, text="Reportes")
        superior = ttk.Frame(self.tab_reportes)
        superior.pack(fill="x", padx=8, pady=8)
        self.combo_reporte = ttk.Combobox(
            superior,
            state="readonly",
            width=55,
            values=(
                "Préstamos activos y material en tránsito",
                "Libros más solicitados entre sedes",
                "Disponibilidad de catálogo por sede",
                "Movimientos y tiempo promedio de tránsito",
            ),
        )
        self.combo_reporte.current(0)
        self.combo_reporte.pack(side="left", padx=4)
        ttk.Button(superior, text="Generar", command=self.generar_reporte).pack(side="left", padx=4)
        self.lbl_reporte = ttk.Label(superior, text="")
        self.lbl_reporte.pack(side="left", padx=12)

        self.frame_reporte = ttk.Frame(self.tab_reportes)
        self.frame_reporte.pack(fill="both", expand=True, padx=8, pady=8)
        self.tree_reporte = None

    def mostrar_reporte(self, columnas, titulos, filas):
        if self.tree_reporte is not None:
            self.tree_reporte.destroy()
        self.tree_reporte = self.crear_tree(self.frame_reporte, columnas, titulos)
        for fila in filas:
            self.tree_reporte.insert("", "end", values=fila)

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
                ("Tipo", "ID/Nro", "Libro", "Ejemplar", "Origen", "Destino", "Vencimiento/Estado"),
                filas,
            )
        elif opcion == 1:
            datos = libros_mas_solicitados_interbibliotecarios()
            self.mostrar_reporte(("isbn", "titulo", "cantidad"), ("ISBN", "Libro", "Solicitudes"), datos)
        elif opcion == 2:
            datos = disponibilidad_catalogo_por_sede()
            self.mostrar_reporte(("sede", "isbn", "titulo", "cantidad"), ("Sede", "ISBN", "Libro", "Disponibles"), datos)
        else:
            datos = movimientos_y_tiempo_promedio_transito()
            self.mostrar_reporte(("origen", "destino", "cantidad"), ("Origen", "Destino", "Envíos"), datos["movimientos"])
            self.lbl_reporte.config(text=f"Promedio de tránsito: {datos['horas_promedio_transito']:.2f} h")

    def refrescar_todo(self):
        sedes = listar_sedes()
        socios = listar_socios()
        libros = listar_libros()
        ejemplares = listar_ejemplares()
        prestamos = listar_prestamos()
        reservas = listar_reservas()
        remitos = listar_remitos()

        self.limpiar_tree(self.tree_sedes)
        for s in sedes:
            self.tree_sedes.insert("", "end", values=(s[0], s[1], s[2], s[3], s[4], s[5], "Activa" if s[6] else "Baja"))

        self.limpiar_tree(self.tree_socios)
        for s in socios:
            self.tree_socios.insert("", "end", values=(s[0], s[1], s[2], s[3], s[4], s[5], "Habilitado" if s[6] else "Inhabilitado"))

        self.limpiar_tree(self.tree_libros)
        for l in libros:
            self.tree_libros.insert("", "end", values=l)

        self.limpiar_tree(self.tree_ejemplares)
        for e in ejemplares:
            self.tree_ejemplares.insert("", "end", values=e)

        self.limpiar_tree(self.tree_prestamos)
        for p in prestamos:
            self.tree_prestamos.insert("", "end", values=p)

        self.limpiar_tree(self.tree_reservas)
        for r in reservas:
            self.tree_reservas.insert("", "end", values=r)

        self.limpiar_tree(self.tree_remitos)
        for r in remitos:
            self.tree_remitos.insert("", "end", values=r)

        sedes_combo = [f"{s[0]} - {s[1]}" for s in sedes if s[6]]
        socios_combo = [f"{s[0]} - {s[2]} {s[3]} ({s[1]})" for s in socios if s[6]]
        libros_combo = [f"{l[0]} - {l[2]} ({l[1]})" for l in libros]
        ejemplares_combo = [f"{e[0]} - {e[2]} / {e[1]} [{e[5]}]" for e in ejemplares]

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
            f"{p[0]} - {p[2]} / {p[3]} / {p[5]} -> {p[6]}" for p in solicitudes
        ]

    def mostrar_resultado(self, titulo, ok, dato):
        if ok:
            messagebox.showinfo(titulo, str(dato))
        else:
            messagebox.showerror(titulo, str(dato))
