# TP Integrador DAO 2026

**Tema 1:** Biblioteca - Sistema de Préstamos Interbibliotecarios

Repositorio del trabajo práctico integrador de Desarrollo de Aplicaciones con Objetos.

## Estado actual

Ya están implementadas las dos primeras etapas de la base:

- clases Sede, Socio, Libro, Ejemplar y Prestamo;
- base SQLite con sedes, socios, libros, ejemplares y préstamos;
- altas, búsquedas y modificaciones básicas;
- control de DNI, ISBN y código de ejemplar duplicados;
- baja lógica de sedes y habilitación de socios;
- préstamo local con validación de socio, sede y ejemplar;
- devolución con actualización del estado físico;
- transacciones para registrar préstamo y devolución;
- pruebas iniciales con pytest.

Todavía no están implementadas reservas, remitos, interfaz ni reportes.

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
