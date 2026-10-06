from modelos.remito import Remito
from patrones.observer import Observer


class ObservadorPrueba(Observer):

    def __init__(self):
        self.estados = []

    def update(self, subject):
        self.estados.append(subject.estado)


def test_remito_notifica_al_cambiar_de_estado():
    remito = Remito("R-001", 1, 2)
    observador = ObservadorPrueba()
    remito.attach(observador)

    assert not remito.cambiar_estado("RECIBIDO")
    assert observador.estados == []

    assert remito.cambiar_estado("DESPACHADO")
    assert remito.cambiar_estado("EN_TRANSITO")
    assert remito.cambiar_estado("RECIBIDO")
    assert observador.estados == ["DESPACHADO", "EN_TRANSITO", "RECIBIDO"]
