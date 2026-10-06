class Ejemplar:

    def __init__(self, codigo, libro, sede_pertenencia, sede_actual=None,
                 estado="DISPONIBLE", estado_fisico="BUENO", id=None):
        self.id = id
        self.codigo = codigo
        self.libro = libro
        self.sede_pertenencia = sede_pertenencia
        self.sede_actual = sede_pertenencia if sede_actual is None else sede_actual
        self.estado = estado
        self.estado_fisico = estado_fisico
