# TP Integrador DAO 2026

**Tema 1:** Biblioteca - Sistema de Préstamos Interbibliotecarios

Aplicación desarrollada en Python con SQLite y una interfaz gráfica en Tkinter/ttk.

## Funcionalidades

- administración de sedes y socios;
- catálogo de libros y ejemplares físicos;
- préstamos locales e interbibliotecarios;
- reservas y devoluciones;
- remitos de ida y retorno con trazabilidad;
- consulta de disponibilidad;
- cinco reportes de gestión;
- patrones Observer y Singleton.

El flujo interbibliotecario mantiene la sede de pertenencia del ejemplar y registra su ubicación actual durante el traslado. Los remitos siguen el ciclo:

`PREPARADO -> DESPACHADO -> EN_TRANSITO -> RECIBIDO`

## Documentación

- `docs/diseno.md`: decisiones principales del modelo y funcionamiento.
- `docs/modelo.puml`: diagrama UML del dominio.
- `docs/der.puml`: modelo relacional.
- `docs/casos-uso.puml`: casos de uso.
- `docs/patrones.puml`: aplicación de Observer y Singleton.

## Estructura

```
modelos/
datos/
patrones/
interfaz/
tests/
docs/
main.py
```

## Ejecución

```bash
python main.py
```

## Pruebas

```bash
python -m pytest -q
```

La suite actual contiene 36 pruebas automatizadas.
