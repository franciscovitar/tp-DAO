class Sede:

    def __init__(self, nombre, direccion, telefono, email, horario, activa=True, id=None):
        self.id = id
        self.nombre = nombre
        self.direccion = direccion
        self.telefono = telefono
        self.email = email
        self.horario = horario
        self.activa = activa
