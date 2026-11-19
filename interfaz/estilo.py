"""Estilo visual de la aplicación.

Se usa el tema "clam" de ttk como base porque respeta los colores que se le
configuran en Windows, Linux y macOS (los temas nativos "vista" y "aqua"
ignoran buena parte de estos ajustes). No requiere dependencias externas.
"""

import tkinter.font as tkfont
from tkinter import ttk

# Paleta sobria: grises cálidos y un verde oscuro apagado como único acento.
FONDO = "#F2F1EE"
SUPERFICIE = "#FFFFFF"
BORDE = "#C9C6BF"
TEXTO = "#1F1F1D"
TEXTO_SECUNDARIO = "#66645E"
ACENTO = "#2F5A4D"
ACENTO_ACTIVO = "#24483D"
SELECCION = "#D5E2DC"
FILA_ALTERNA = "#F7F6F3"
ENCABEZADO_TABLA = "#E5E3DD"
BOTON = "#E8E6E1"
BOTON_ACTIVO = "#DDDAD3"
ERROR = "#9A2B2B"

TAMANIO_BASE = 10


def aplicar_estilo(raiz):
    base = tkfont.nametofont("TkDefaultFont")
    base.configure(size=TAMANIO_BASE)
    for nombre in ("TkTextFont", "TkMenuFont", "TkHeadingFont"):
        tkfont.nametofont(nombre).configure(family=base.cget("family"), size=TAMANIO_BASE)

    familia = base.cget("family")
    negrita = (familia, TAMANIO_BASE, "bold")
    titulo = (familia, TAMANIO_BASE + 4, "bold")

    raiz.configure(background=FONDO)
    raiz.option_add("*TCombobox*Listbox.background", SUPERFICIE)
    raiz.option_add("*TCombobox*Listbox.foreground", TEXTO)
    raiz.option_add("*TCombobox*Listbox.selectBackground", SELECCION)
    raiz.option_add("*TCombobox*Listbox.selectForeground", TEXTO)
    raiz.option_add("*TCombobox*Listbox.font", base)

    estilo = ttk.Style(raiz)
    estilo.theme_use("clam")

    estilo.configure(
        ".",
        background=FONDO,
        foreground=TEXTO,
        font=base,
        bordercolor=BORDE,
        lightcolor=FONDO,
        darkcolor=FONDO,
        troughcolor=FONDO,
        focuscolor=ACENTO,
        selectbackground=SELECCION,
        selectforeground=TEXTO,
    )

    estilo.configure("TFrame", background=FONDO)
    estilo.configure("TLabel", background=FONDO, foreground=TEXTO)
    estilo.configure("Titulo.TLabel", font=titulo)
    estilo.configure("Ayuda.TLabel", foreground=TEXTO_SECUNDARIO)
    estilo.configure("Campo.TLabel", foreground=TEXTO)
    estilo.configure("Error.TLabel", foreground=ERROR)
    estilo.configure("BarraEstado.TFrame", background=ENCABEZADO_TABLA)
    estilo.configure("BarraEstado.TLabel", background=ENCABEZADO_TABLA, foreground=TEXTO_SECUNDARIO,
                     padding=(12, 4))

    estilo.configure("TLabelframe", background=FONDO, bordercolor=BORDE, relief="solid", borderwidth=1)
    estilo.configure("TLabelframe.Label", background=FONDO, foreground=TEXTO, font=negrita)

    estilo.configure("TNotebook", background=FONDO, borderwidth=0, tabmargins=(0, 0, 0, 0))
    estilo.configure("TNotebook.Tab", background=BOTON, foreground=TEXTO_SECUNDARIO,
                     padding=(16, 7), bordercolor=BORDE, lightcolor=BOTON)
    estilo.map(
        "TNotebook.Tab",
        background=[("selected", FONDO), ("active", BOTON_ACTIVO)],
        foreground=[("selected", TEXTO)],
        lightcolor=[("selected", FONDO)],
        font=[("selected", negrita)],
    )

    estilo.configure("TEntry", fieldbackground=SUPERFICIE, bordercolor=BORDE,
                     lightcolor=SUPERFICIE, darkcolor=SUPERFICIE, padding=(5, 4))
    estilo.map("TEntry", bordercolor=[("focus", ACENTO)], lightcolor=[("focus", ACENTO)])

    estilo.configure("TCombobox", fieldbackground=SUPERFICIE, background=BOTON, bordercolor=BORDE,
                     lightcolor=SUPERFICIE, darkcolor=SUPERFICIE, arrowcolor=TEXTO_SECUNDARIO,
                     padding=(5, 4))
    estilo.map(
        "TCombobox",
        fieldbackground=[("readonly", SUPERFICIE)],
        selectbackground=[("readonly", SUPERFICIE)],
        selectforeground=[("readonly", TEXTO)],
        bordercolor=[("focus", ACENTO)],
        background=[("active", BOTON_ACTIVO)],
    )

    estilo.configure("TButton", background=BOTON, foreground=TEXTO, bordercolor=BORDE,
                     lightcolor=BOTON, darkcolor=BOTON, padding=(14, 5), focusthickness=1)
    estilo.map(
        "TButton",
        background=[("pressed", BOTON_ACTIVO), ("active", BOTON_ACTIVO)],
        lightcolor=[("active", BOTON_ACTIVO)],
        darkcolor=[("active", BOTON_ACTIVO)],
    )
    estilo.configure("Primario.TButton", background=ACENTO, foreground=SUPERFICIE, bordercolor=ACENTO,
                     lightcolor=ACENTO, darkcolor=ACENTO, font=negrita)
    estilo.map(
        "Primario.TButton",
        background=[("pressed", ACENTO_ACTIVO), ("active", ACENTO_ACTIVO)],
        lightcolor=[("active", ACENTO_ACTIVO)],
        darkcolor=[("active", ACENTO_ACTIVO)],
        foreground=[("disabled", BORDE)],
    )

    alto_fila = base.metrics("linespace") + 10
    estilo.configure("Treeview", background=SUPERFICIE, fieldbackground=SUPERFICIE, foreground=TEXTO,
                     bordercolor=BORDE, lightcolor=SUPERFICIE, darkcolor=SUPERFICIE, rowheight=alto_fila)
    estilo.map("Treeview", background=[("selected", SELECCION)], foreground=[("selected", TEXTO)])
    estilo.configure("Treeview.Heading", background=ENCABEZADO_TABLA, foreground=TEXTO, font=negrita,
                     bordercolor=BORDE, lightcolor=ENCABEZADO_TABLA, darkcolor=ENCABEZADO_TABLA,
                     relief="flat", padding=(6, 5))
    estilo.map("Treeview.Heading", background=[("active", BOTON_ACTIVO)])

    estilo.configure("Vertical.TScrollbar", background=BOTON, troughcolor=FONDO, bordercolor=FONDO,
                     arrowcolor=TEXTO_SECUNDARIO, lightcolor=BOTON, darkcolor=BOTON)
    estilo.configure("Horizontal.TScrollbar", background=BOTON, troughcolor=FONDO, bordercolor=FONDO,
                     arrowcolor=TEXTO_SECUNDARIO, lightcolor=BOTON, darkcolor=BOTON)
    return estilo
