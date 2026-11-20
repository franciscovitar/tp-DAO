from datos.base_datos import DatabaseSingleton


def test_database_singleton_devuelve_la_misma_instancia():
    db1 = DatabaseSingleton("test_singleton.db")
    db2 = DatabaseSingleton("test_singleton.db")

    assert db1 is db2
    db1.close_connection()


def test_las_operaciones_comparten_una_unica_conexion():
    from datos.base_datos import conectar, crear_tablas
    from datos.sedes import agregar_sede, listar_sedes
    from modelos.sede import Sede

    crear_tablas("test_singleton.db")
    conexion = conectar("test_singleton.db")
    agregar_sede(Sede("Centro", "Colon 100", "", "", ""), "test_singleton.db")
    listar_sedes("test_singleton.db")

    # Después de varias operaciones sigue siendo la misma conexión, abierta
    assert conectar("test_singleton.db") is conexion
    conexion.execute("SELECT 1")
    DatabaseSingleton().close_connection()
    import os
    os.remove("test_singleton.db")
