# TP Integrador DAO 2026

**Tema 1:** Biblioteca - Sistema de Préstamos Interbibliotecarios

## Estado actual

Implementado:
- modelo principal y persistencia SQLite;
- préstamo local, devolución y reservas;
- solicitud interbibliotecaria;
- remitos de ida y retorno con trazabilidad;
- Observer aplicado al historial del Remito;
- Singleton para acceso a SQLite;
- cuatro reportes obligatorios más préstamos vencidos;
- interfaz gráfica con Tkinter/ttk;
- UML, DER, casos de uso y diagramas de patrones.

La interfaz permite trabajar con sedes, socios, catálogo, ejemplares, préstamos, reservas, remitos y reportes.

## Documentación

- `docs/estado-actual.md`: checkpoint para retomar el TP.
- `docs/auditoria-consigna.md`: cobertura requisito por requisito.
- `docs/prueba-manual.md`: recorrido de prueba antes de entregar.
- `docs/defensa.md`: decisiones que hay que poder explicar.
- `docs/modelo.puml`: UML del dominio.
- `docs/der.puml`: modelo relacional.
- `docs/casos-uso.puml`: casos de uso.
- `docs/patrones.puml`: Observer y Singleton.

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
