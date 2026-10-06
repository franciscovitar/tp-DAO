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

- El núcleo anterior tenía 26 tests registrados como aprobados.
- La interfaz base fue validada por sintaxis y se verificó el import de tkinter.
- El flujo de ida y retorno fue ejecutado localmente después de aplicar Observer al historial y pasó.
- La consulta SQL del reporte de vencidos fue ejecutada localmente y pasó.
- La activación/desactivación de ejemplares y el bloqueo durante un préstamo fueron verificados con una prueba dirigida local.
- El flujo interbibliotecario con PENDIENTE_RETORNO, exclusión del reporte de disponibilidad y regreso a la sede de pertenencia fue ejecutado de punta a punta en una prueba dirigida local.
- La suite actual contiene 35 tests.
- Las nuevas guardas de duración, estado físico y número de remito fueron revisadas con pruebas específicas; falta ejecutar la regresión completa de los 35 tests sobre el main actual.
- Falta una ejecución visual completa de la interfaz.

## Pendiente inmediato

1. Ejecutar la interfaz visualmente de punta a punta.
2. Reejecutar regresión completa.
3. Revisar casos límite finales.
4. Preparar defensa.
