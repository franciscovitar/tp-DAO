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
- Historial append-only.
- Recepción con actualización de sede_actual.
- Activación del préstamo interbibliotecario luego de recibir.
- Retorno del ejemplar interbibliotecario mediante un segundo remito.
- Observer para cambios del Remito.
- DatabaseSingleton para SQLite.
- Cuatro reportes no triviales.
- Interfaz gráfica para sedes, socios, catálogo, préstamos, reservas, remitos, retorno y reportes.

## Regla de retorno adoptada

Después de la devolución de un préstamo interbibliotecario se genera un remito desde la sede de devolución hacia la sede de pertenencia. Al crear ese remito el ejemplar deja de estar disponible; al recibirlo vuelve a sede_pertenencia y queda DISPONIBLE.

Esta regla completa un punto que la consigna deja abierto y se documenta como decisión de diseño del grupo.

## Verificación

- El núcleo anterior tenía 26 tests registrados como aprobados.
- La interfaz base fue validada por sintaxis y se verificó el import de tkinter.
- El flujo de retorno fue ejecutado localmente de punta a punta y pasó.
- El retorno ya está expuesto en la interfaz.
- Falta una ejecución visual completa de la interfaz y una regresión completa después de los últimos cambios.

## Pendiente inmediato

1. Ejecutar la interfaz visualmente de punta a punta.
2. Reejecutar regresión completa.
3. Revisar casos límite finales.
4. Actualizar UML/DER final.
5. Preparar defensa.
