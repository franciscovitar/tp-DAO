# Estado actual del TP

Actualizado: 2026-10-06

## Decisiones canónicas

- Tema: Biblioteca - Sistema de Préstamos Interbibliotecarios.
- Repositorio: franciscovitar/tp-DAO.
- Código en Python + SQLite.
- Mantener el nivel y estilo de la cátedra; evitar sobreingeniería.
- Patrones enseñados en el material 2026 recibido: Singleton, Factory y Observer.
- Patrones elegidos e implementados: Observer + Singleton.
- State descartado; Factory queda como alternativa.

## Implementado

- Sede, Socio, Libro, Ejemplar, Prestamo, Reserva y Remito.
- Préstamo local, devolución y reservas.
- Solicitud de préstamo interbibliotecario.
- Remito con PREPARADO -> DESPACHADO -> EN_TRANSITO -> RECIBIDO.
- Historial de remito append-only.
- Recepción con actualización de sede_actual.
- Activación del préstamo interbibliotecario luego de recibir.
- Observer para monitoreo de cambios del Remito.
- DatabaseSingleton para centralizar el acceso a SQLite.
- Cuatro reportes no triviales.

## Verificación

Checkpoint actual probado localmente: 26 tests pasaron.

## Pendiente inmediato

1. Resolver o validar el retorno del ejemplar a sede de pertenencia después de una devolución interbibliotecaria.
2. Implementar interfaz.
3. Hacer auditoría requisito por requisito.
4. Preparar defensa.

## Punto abierto

El retorno del ejemplar luego de una devolución interbibliotecaria no está definido expresamente en la consigna. No fijarlo como regla definitiva hasta validarlo con el profesor o material oficial.
