from datos.base_datos import DatabaseSingleton


def test_database_singleton_devuelve_la_misma_instancia():
    db1 = DatabaseSingleton("test_singleton.db")
    db2 = DatabaseSingleton("test_singleton.db")

    assert db1 is db2
    db1.close_connection()
