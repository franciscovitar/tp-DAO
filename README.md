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
- pruebas con pytest.

Los dos patrones obligatorios y los cuatro reportes obligatorios ya están cubiertos.

Ver `docs/estado-actual.md` para retomar el trabajo sin depender del historial del chat.

## Estructura

```
modelos/
datos/
patrones/
tests/
docs/
main.py
```

## Ejecución

```
python main.py
python -m pytest -q
```
