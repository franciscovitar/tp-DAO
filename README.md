# TP Integrador DAO 2026

**Tema 1:** Biblioteca - Sistema de Préstamos Interbibliotecarios

Repositorio del trabajo práctico integrador de Desarrollo de Aplicaciones con Objetos.

## Estado actual

Está terminada la primera base del proyecto:

- clases Sede, Socio, Libro y Ejemplar;
- base SQLite con las cuatro tablas iniciales;
- altas, búsquedas y modificaciones básicas;
- control de DNI, ISBN y código de ejemplar duplicados;
- baja lógica de sedes y habilitación de socios;
- pruebas iniciales con pytest.

Todavía no están implementados préstamos, reservas, remitos, interfaz ni reportes.

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
