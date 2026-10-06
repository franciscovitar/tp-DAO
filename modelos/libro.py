class Libro:

    def __init__(self, isbn, titulo, autor, editorial, anio, id=None):
        self.id = id
        self.isbn = isbn
        self.titulo = titulo
        self.autor = autor
        self.editorial = editorial
        self.anio = anio
