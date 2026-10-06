# TP Integrador DAO 2026

**Tema 1:** Biblioteca - Sistema de Préstamos Interbibliotecarios

## Estado actual

Implementado:
- modelo principal y persistencia SQLite;
- préstamo local, devolución y reservas;
- solicitud interbibliotecaria y remitos con trazabilidad;
- Observer para monitoreo del Remito;
- Singleton para acceso a SQLite;
- cuatro reportes no triviales;
- primera interfaz gráfica con Tkinter/ttk.

La interfaz permite trabajar con sedes, socios, catálogo, ejemplares, préstamos, reservas, remitos y reportes.

Ver `docs/estado-actual.md` para retomar el trabajo sin depender del historial del chat.

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

```
python main.py
```

Pruebas:

```
python -m pytest -q
```
