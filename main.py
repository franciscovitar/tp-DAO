from datos.base_datos import crear_tablas
from interfaz.app import BibliotecaApp


def main():
    crear_tablas()
    app = BibliotecaApp()
    app.mainloop()


if __name__ == "__main__":
    main()
