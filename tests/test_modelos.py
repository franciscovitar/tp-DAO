from modelos.sede import Sede
from modelos.socio import Socio
from modelos.libro import Libro
from modelos.ejemplar import Ejemplar


def test_sede_nueva_esta_activa():
    sede = Sede("Centro", "Av. Siempre Viva 123", "1234", "centro@biblioteca.com", "8 a 20")
    assert sede.activa is True


def test_socio_nuevo_esta_habilitado():
    socio = Socio("40111222", "Ana", "Perez", "351111111", "ana@mail.com")
    assert socio.habilitado is True


def test_ejemplar_nuevo_esta_disponible_en_su_sede():
    sede = Sede("Centro", "Av. Siempre Viva 123", "1234", "centro@biblioteca.com", "8 a 20")
    libro = Libro("9789500000001", "Libro de prueba", "Autor", "Editorial", 2020)
    ejemplar = Ejemplar("EJ-001", libro, sede)

    assert ejemplar.estado == "DISPONIBLE"
    assert ejemplar.estado_fisico == "BUENO"
    assert ejemplar.sede_actual == sede


def test_prestamo_vencido_se_calcula_por_fecha():
    from datetime import date, timedelta
    from modelos.prestamo import Prestamo

    sede = Sede("Centro", "Colon 100", "111", "centro@mail.com", "8 a 20")
    socio = Socio("40111222", "Ana", "Perez", "111", "ana@mail.com")
    libro = Libro("9789500000001", "Uno", "Autor", "Editorial", 2020)
    ejemplar = Ejemplar("EJ-001", libro, sede)
    prestamo = Prestamo(socio, ejemplar, sede, sede, date.today(),
                        date.today() - timedelta(days=20),
                        date.today() - timedelta(days=6))

    assert prestamo.esta_vencido()
