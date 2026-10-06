# TP Integrador DAO 2026

**Tema 1:** Biblioteca - Sistema de Préstamos Interbibliotecarios

Repositorio del trabajo práctico integrador de Desarrollo de Aplicaciones con Objetos.

## Estado actual

Ya están implementadas las tres primeras etapas de la base:

- clases Sede, Socio, Libro, Ejemplar, Prestamo y Reserva;
- base SQLite con sedes, socios, libros, ejemplares, préstamos y reservas;
- altas, búsquedas y modificaciones básicas;
- control de DNI, ISBN y código de ejemplar duplicados;
- baja lógica de sedes y habilitación de socios;
- préstamo local con validación de socio, sede y ejemplar;
- devolución con actualización del estado físico;
- reservas, cancelación y concreción del préstamo por el socio que reservó;
- transacciones para los cambios que afectan más de una tabla;
- pruebas iniciales con pytest.

Todavía no están implementados remitos, interfaz ni reportes.

## Estructura

```
modelos/
datos/
tests/
docs/
main.py
```

## Ejecución

Para crear la base de datos:

```
python main.py
```

Para ejecutar las pruebas:

```
python -m pytest -q
```
