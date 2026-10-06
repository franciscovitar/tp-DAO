# TP Integrador DAO 2026

**Tema 1:** Biblioteca - Sistema de Préstamos Interbibliotecarios

## Estado actual

Ya están implementados:

- Sede, Socio, Libro, Ejemplar, Prestamo, Reserva y Remito;
- persistencia SQLite;
- préstamo local y devolución;
- reservas;
- solicitud de préstamo interbibliotecario;
- remitos con estados PREPARADO, DESPACHADO, EN_TRANSITO y RECIBIDO;
- historial de estados;
- actualización de ubicación del ejemplar;
- activación del préstamo al llegar a destino;
- patrón Observer aplicado al monitoreo del remito;
- pruebas con pytest.

Patrones definidos para el TP:
- Observer: implementado.
- Singleton: próximo bloque.
- Factory: alternativa si aparece una necesidad real.

Ver docs/estado-actual.md para retomar el trabajo sin depender del historial del chat.

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
