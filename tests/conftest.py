import pytest

from datos.base_datos import DatabaseSingleton


@pytest.fixture(autouse=True)
def cerrar_conexion_al_terminar():
    """Cierra la conexión compartida del Singleton después de cada prueba,
    para que el archivo de la base de prueba se pueda borrar (en Windows no
    se puede borrar un archivo SQLite que sigue abierto)."""
    yield
    DatabaseSingleton._instance and DatabaseSingleton._instance.close_connection()
