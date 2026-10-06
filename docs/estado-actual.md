# Estado actual del TP

Actualizado: 2026-10-06

## Decisiones canónicas

- Tema: Biblioteca - Sistema de Préstamos Interbibliotecarios.
- Repositorio: franciscovitar/tp-DAO.
- Código en Python + SQLite.
- Mantener el nivel y estilo de la cátedra; evitar sobreingeniería.
- Patrones elegidos e implementados: Observer + Singleton.
- State descartado; Factory queda como alternativa.
- Interfaz: Tkinter/ttk como decisión técnica mínima porque las fuentes disponibles exigen interfaz gráfica pero no prescriben toolkit.

## Implementado

- Sede, Socio, Libro, Ejemplar, Prestamo, Reserva y Remito.
- Préstamo local, devolución y reservas.
- Solicitud de préstamo interbibliotecario.
- Remito con PREPARADO -> DESPACHADO -> EN_TRANSITO -> RECIBIDO.
- Historial append-only registrado mediante Observer.
- Recepción con actualización de sede_actual.
- Activación del préstamo interbibliotecario luego de recibir.
- Retorno del ejemplar interbibliotecario mediante un segundo remito.
- Estado PENDIENTE_RETORNO entre la devolución interbibliotecaria y el despacho de regreso, evitando que el ejemplar figure como disponible en la sede destino.
- Observer para cambios del Remito.
- DatabaseSingleton para SQLite.
- Cuatro reportes no triviales obligatorios más un reporte de préstamos vencidos.
- Interfaz gráfica para sedes, socios, catálogo, ejemplares, préstamos, reservas, remitos, retorno y reportes.
- Activación/desactivación administrativa de ejemplares, bloqueada mientras estén reservados, prestados o en tránsito.

## Regla de retorno adoptada

Después de la devolución de un préstamo interbibliotecario el ejemplar queda PENDIENTE_RETORNO y deja de figurar como disponible. Luego se genera un remito desde la sede de devolución hacia la sede de pertenencia; al recibirlo vuelve a sede_pertenencia y queda DISPONIBLE.

Esta regla completa un punto que la consigna deja abierto y se documenta como decisión de diseño del grupo.

## Verificación

- Regresión completa ejecutada sobre el código funcional de main: **36 tests aprobados en 0.65 s**.
- Verificación realizada en GitHub Actions, run `37543370547`.
- Smoke funcional de la interfaz ejecutado bajo Xvfb y finalizado con `GUI_SMOKE_OK`.
- El smoke recorrió las 7 pestañas y ejercitó: altas de sedes/socio/libro/ejemplares, reserva y cancelación, préstamo local y devolución, solicitud interbibliotecaria, remito de ida completo, activación y devolución, remito de retorno completo y generación de los 5 reportes.
- Se comprobó al final que el ejemplar interbibliotecario vuelve a su sede de pertenencia en estado DISPONIBLE y que el historial del remito conserva PREPARADO -> DESPACHADO -> EN_TRANSITO -> RECIBIDO.
- La captura de apertura de la GUI mostró un recorte en los botones de Sedes; se ajustó el layout de acciones de Sedes y Socios a una segunda fila. El cambio es solamente de disposición visual y no modifica reglas de negocio.

## Pendiente inmediato

1. Revisión estética rápida en el escritorio donde se vaya a presentar.
2. Practicar la defensa oral.
