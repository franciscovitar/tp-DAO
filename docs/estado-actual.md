# Estado actual del TP

Actualizado: 2026-10-06

## Decisiones canónicas

- Tema: Biblioteca - Sistema de Préstamos Interbibliotecarios.
- Repositorio: franciscovitar/tp-DAO.
- Código en Python + SQLite.
- Mantener el nivel y estilo de la cátedra; evitar sobreingeniería.
- Patrones enseñados en el material 2026 recibido: Singleton, Factory y Observer.
- Patrones elegidos para el TP: Observer + Singleton.
- State queda descartado porque no aparece en el material de patrones recibido.
- Factory queda como alternativa, no como requisito propio.

## Implementado

- Sede, Socio, Libro, Ejemplar, Prestamo y Reserva.
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

## Verificación

Checkpoint de remitos/Observer probado localmente antes de subir: 19 tests pasaron.

## Pendiente inmediato

1. Implementar Singleton para el acceso a SQLite siguiendo el DatabaseSingleton de la cátedra.
2. Resolver/validar retorno del ejemplar a sede de pertenencia después de una devolución interbibliotecaria.
3. Implementar los cuatro reportes.
4. Luego avanzar con interfaz.

## Punto abierto

El retorno del ejemplar luego de una devolución interbibliotecaria no está definido expresamente en la consigna. No fijarlo como regla definitiva hasta validarlo con el profesor o material oficial.
