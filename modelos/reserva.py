class Reserva:

    def __init__(self, socio, ejemplar, sede, fecha, estado="ACTIVA", id=None):
        self.id = id
        self.socio = socio
        self.ejemplar = ejemplar
        self.sede = sede
        self.fecha = fecha
        self.estado = estado
