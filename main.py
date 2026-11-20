from datos.base_datos import crear_tablas, DatabaseSingleton
from interfaz.app import BibliotecaApp


def main():
    crear_tablas()
    app = BibliotecaApp()
    try:
        app.mainloop()
    finally:
        # La única conexión compartida se cierra al salir de la aplicación.
        DatabaseSingleton().close_connection()


if __name__ == "__main__":
    main()
