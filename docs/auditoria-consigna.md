# Auditoría de la consigna - Tema 1

Actualizada: 2026-10-06

## Procesos obligatorios

1. Administrar sedes: cubierto con alta, modificación y activo/baja.
2. Administrar socios: cubierto con alta, modificación y habilitación/inhabilitación.
3. Administrar catálogo y ejemplares: cubierto con libros, ejemplares, sede de pertenencia y sede actual.
4. Préstamos locales e interbibliotecarios: cubierto.
5. Empaquetar, despachar y recibir con remito y trazabilidad: cubierto con PREPARADO -> DESPACHADO -> EN_TRANSITO -> RECIBIDO.
6. Consultar disponibilidad: cubierto por estado de ejemplares y reporte por sede.
7. Reservas: cubierto con alta, cancelación y concreción.
8. Devoluciones y estado físico: cubierto.

## Validaciones

- No prestar ejemplares no disponibles: cubierta.
- No prestar a socios inhabilitados: cubierta.
- Controlar vencimientos: se guarda la fecha de vencimiento y existe un reporte de préstamos activos vencidos.
- Mantener trazabilidad: cubierta con historial append-only registrado por Observer.
- Evitar duplicados de socios, catálogo y ejemplares: cubierta.
- No prestar ejemplares que no pertenezcan a la sede origen: cubierta.
- No iniciar operaciones hacia o desde sedes de baja: cubierta.

## Patrones

- Observer: Remito es el Subject y HistorialRemitoObserver registra cada transición.
- Singleton: DatabaseSingleton centraliza el acceso a SQLite.

Factory queda fuera porque no resuelve una necesidad actual.

## Reportes

Los cuatro mínimos están cubiertos:
1. préstamos activos y material en tránsito;
2. libros más solicitados entre sedes;
3. disponibilidad por sede;
4. movimientos entre sedes y tiempo promedio de tránsito.

Se agrega un quinto reporte: préstamos vencidos. No se calculan multas porque la consigna no define monto ni regla de cálculo.

## Regla definida por el grupo: retorno

La consigna no determina qué ocurre después de devolver en la sede destino un ejemplar interbibliotecario.

Se adopta esta regla:
1. el socio devuelve el ejemplar en la sede destino;
2. el préstamo queda DEVUELTO;
3. se prepara otro remito hacia la sede de pertenencia;
4. durante el retorno el ejemplar no queda disponible;
5. al recibirlo vuelve a sede_pertenencia y queda DISPONIBLE.

La interfaz permite seleccionar los préstamos interbibliotecarios ya devueltos que todavía no tienen remito de retorno y generar ese remito.

## Pendientes antes del cierre

- ejecutar la interfaz visualmente de punta a punta;
- reejecutar toda la suite después de los últimos cambios;
- revisar casos límite finales;
- actualizar DER/UML y casos de uso finales;
- preparar defensa.
