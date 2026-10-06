from datetime import datetime

from patrones.observer import Subject


class Remito(Subject):

    TRANSICIONES = {
        "PREPARADO": "DESPACHADO",
        "DESPACHADO": "EN_TRANSITO",
        "EN_TRANSITO": "RECIBIDO"
    }

    def __init__(self, numero, sede_origen, sede_destino, ejemplares=None,
                 fecha_creacion=None, fecha_despacho=None,
                 fecha_recepcion=None, estado="PREPARADO", id=None):
        super().__init__()
        self.id = id
        self.numero = numero
        self.sede_origen = sede_origen
        self.sede_destino = sede_destino
        self.ejemplares = [] if ejemplares is None else ejemplares
        self.fecha_creacion = datetime.now() if fecha_creacion is None else fecha_creacion
        self.fecha_despacho = fecha_despacho
        self.fecha_recepcion = fecha_recepcion
        self.estado = estado

    def puede_cambiar_a(self, nuevo_estado):
        return self.TRANSICIONES.get(self.estado) == nuevo_estado

    def cambiar_estado(self, nuevo_estado):
        if not self.puede_cambiar_a(nuevo_estado):
            return False

        self.estado = nuevo_estado
        ahora = datetime.now()

        if nuevo_estado == "DESPACHADO":
            self.fecha_despacho = ahora
        elif nuevo_estado == "RECIBIDO":
            self.fecha_recepcion = ahora

        self.notify()
        return True
