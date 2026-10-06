class Socio:

    def __init__(self, dni, nombre, apellido, telefono, email, habilitado=True, id=None):
        self.id = id
        self.dni = dni
        self.nombre = nombre
        self.apellido = apellido
        self.telefono = telefono
        self.email = email
        self.habilitado = habilitado
