# Estado actual del TP

Actualizado: 2026-10-06

## Decisiones canónicas

- Tema: Biblioteca - Sistema de Préstamos Interbibliotecarios.
- Repositorio: franciscovitar/tp-DAO.
- Código en Python + SQLite.
- Mantener el nivel y estilo de la cátedra; evitar sobreingeniería.
- Patrones enseñados en el material 2026 recibido: Singleton, Factory y Observer.
- Patrones elegidos e implementados: Observer + Singleton.
- State queda descartado porque no aparece en el material de patrones recibido.
- Factory queda como alternativa, no como requisito propio.

## Implementado

- Sede, Socio, Libro, Ejemplar, Prestamo, Reserva y Remito.
- SQLite y operaciones básicas.
- Duplicados de DNI, ISBN y código de ejemplar.
- Préstamo local y devolución.
- Reservas.
- Solicitud de préstamo interbibliotecario.
- Remito y tablas de trazabilidad.
- Flujo PREPARADO -> DESPACHADO -> EN_TRANSITO -> RECIBIDO.
- Historial de remito append-only.
- Recepción actualiza sede_actual.
- Activación del préstamo interbibliotecario después de recibir.
- Observer aplicado a cambios de Remito.
- DatabaseSingleton como punto único de acceso a la conexión SQLite.

## Verificación

Checkpoint con Singleton probado localmente: 22 tests pasaron.

## Pendiente inmediato

1. Implementar los cuatro reportes no triviales.
2. Resolver/validar retorno del ejemplar a sede de pertenencia después de una devolución interbibliotecaria.
3. Luego avanzar con interfaz y auditoría final.

## Punto abierto

El retorno del ejemplar luego de una devolución interbibliotecaria no está definido expresamente en la consigna. No fijarlo como regla definitiva hasta validarlo con el profesor o material oficial.
