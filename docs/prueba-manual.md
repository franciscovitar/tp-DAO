# Checklist de prueba manual

Usar esta guía antes de la entrega y la defensa.

## Preparación

1. Ejecutar `python main.py`.
2. Confirmar que abre la ventana principal sin errores.
3. Trabajar con una base nueva o con datos de prueba identificables.

## Sedes

- Crear Sede Centro.
- Crear Sede Norte.
- Modificar un dato.
- Dar de baja una sede y comprobar que las operaciones que la usan son rechazadas.
- Volver a dejar activas las sedes para continuar.

## Socios

- Crear un socio habilitado.
- Intentar crear otro con el mismo DNI.
- Inhabilitarlo y comprobar que no puede pedir préstamos ni reservas.
- Habilitarlo nuevamente.

## Catálogo y ejemplares

- Crear un libro.
- Intentar repetir el ISBN.
- Crear un ejemplar en Sede Centro.
- Intentar repetir su código.
- Verificar que figura DISPONIBLE y con Centro como sede de pertenencia y sede actual.
- Desactivar el ejemplar y verificar que queda BAJA.
- Reactivarlo y verificar que vuelve a DISPONIBLE.
- Con un ejemplar prestado, comprobar que la interfaz no permite desactivarlo.

## Préstamo local

- Registrar un préstamo local.
- Verificar que queda ACTIVO y el ejemplar PRESTADO.
- Intentar prestarlo nuevamente.
- Registrar la devolución.
- Elegir un estado físico y comprobar que queda guardado.

## Reserva

- Reservar un ejemplar disponible.
- Verificar que queda RESERVADO.
- Comprobar que otro socio no puede tomarlo.
- Cancelar una reserva y verificar que vuelve a DISPONIBLE.
- Repetir y concretar el préstamo con el socio que reservó.

## Préstamo interbibliotecario

Con un ejemplar perteneciente a Centro y Norte como destino:

1. registrar la solicitud;
2. comprobar que el préstamo queda SOLICITADO;
3. crear remito de ida;
4. intentar saltar directamente a RECIBIDO y verificar rechazo;
5. pasar por DESPACHADO;
6. pasar por EN_TRANSITO;
7. pasar por RECIBIDO;
8. revisar el historial;
9. comprobar que sede_actual ahora es Norte;
10. activar el préstamo;
11. registrar la devolución en Norte;
12. comprobar que el ejemplar queda PENDIENTE_RETORNO y que no aparece como disponible;
13. crear remito de retorno;
14. avanzar PREPARADO -> DESPACHADO -> EN_TRANSITO -> RECIBIDO;
15. comprobar que sede_actual vuelve a Centro y el ejemplar queda DISPONIBLE.

## Reportes

Comprobar que abren y muestran datos coherentes:

- préstamos activos y material en tránsito;
- libros más solicitados entre sedes;
- disponibilidad por sede;
- movimientos y tiempo promedio de tránsito;
- préstamos vencidos.

Para probar vencidos se puede usar un dato de prueba con una fecha de vencimiento anterior a la fecha actual.

## Cierre

Antes de entregar:

- no debe haber excepciones en consola durante el recorrido;
- los mensajes de error deben ser entendibles;
- ningún estado debe quedar incoherente después de un error;
- el historial de un remito debe conservar todas las transiciones;
- las sedes de baja no deben participar en operaciones nuevas;
- los identificadores únicos no deben admitir duplicados.
