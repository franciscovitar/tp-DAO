# TP Integrador DAO 2026

**Tema 1:** Biblioteca - Sistema de Préstamos Interbibliotecarios

## Estado actual

Ya están implementados:

- Sede, Socio, Libro, Ejemplar, Prestamo, Reserva y Remito;
- persistencia SQLite;
- préstamo local y devolución;
- reservas;
- solicitud de préstamo interbibliotecario;
- remitos con trazabilidad completa de estados;
- actualización de ubicación del ejemplar;
- activación del préstamo al llegar a destino;
- patrón Observer para monitoreo del Remito;
- patrón Singleton para centralizar el acceso a SQLite;
- pruebas con pytest.

Los dos patrones obligatorios ya están implementados.

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
