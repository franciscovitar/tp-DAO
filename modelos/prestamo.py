from datetime import date


class Prestamo:

    def __init__(self, socio, ejemplar, sede_origen, sede_destino,
                 fecha_solicitud, fecha_inicio, fecha_vencimiento,
                 fecha_devolucion=None, estado="ACTIVO", id=None):
        self.id = id
        self.socio = socio
        self.ejemplar = ejemplar
        self.sede_origen = sede_origen
        self.sede_destino = sede_destino
        self.fecha_solicitud = fecha_solicitud
        self.fecha_inicio = fecha_inicio
        self.fecha_vencimiento = fecha_vencimiento
        self.fecha_devolucion = fecha_devolucion
        self.estado = estado

    def esta_vencido(self):
        return self.estado == "ACTIVO" and self.fecha_vencimiento < date.today()
