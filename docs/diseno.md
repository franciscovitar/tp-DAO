# Diseño del sistema

## Modelo principal

El sistema distingue el catálogo de las copias físicas.

- **Sede:** dirección, contacto, horario y estado activa/baja.
- **Socio:** datos personales y estado habilitado/inhabilitado.
- **Libro:** información de catálogo.
- **Ejemplar:** copia física de un libro, con código propio, sede de pertenencia, sede actual, estado y estado físico.
- **Prestamo:** préstamo local o interbibliotecario.
- **Reserva:** reserva de un ejemplar para un socio.
- **Remito:** traslado de un ejemplar entre sedes.

Un Libro puede tener varios Ejemplares. La sede de pertenencia indica a qué biblioteca pertenece la copia; la sede actual indica dónde se encuentra físicamente en cada momento.

## Estados principales

### Ejemplar

- DISPONIBLE
- RESERVADO
- PRESTADO
- PENDIENTE_RETORNO
- EN_TRANSITO
- BAJA

### Prestamo

- SOLICITADO
- ACTIVO
- DEVUELTO

### Reserva

- ACTIVA
- CUMPLIDA
- CANCELADA

### Remito

- PREPARADO
- DESPACHADO
- EN_TRANSITO
- RECIBIDO

El Remito sólo puede avanzar en ese orden. Cada cambio de estado agrega un registro al historial para conservar la trazabilidad.

## Préstamo local

Para registrar un préstamo local se verifica que:

- el socio exista y esté habilitado;
- la sede esté activa;
- el ejemplar esté disponible o reservado para ese mismo socio;
- el ejemplar pertenezca y se encuentre en la sede del préstamo.

Al registrarlo, el préstamo queda ACTIVO y el ejemplar pasa a PRESTADO.

## Préstamo interbibliotecario

1. El socio solicita un ejemplar disponible de otra sede.
2. El préstamo queda SOLICITADO y el ejemplar RESERVADO.
3. Se crea un remito en estado PREPARADO.
4. Al despacharlo, el ejemplar pasa a EN_TRANSITO.
5. El remito avanza por DESPACHADO y EN_TRANSITO.
6. Al recibirlo, se actualiza la sede actual del ejemplar y queda RESERVADO para el socio que lo pidió.
7. El préstamo se activa cuando el ejemplar ya está en la sede destino.
8. Al devolverlo, el préstamo queda DEVUELTO y el ejemplar pasa a PENDIENTE_RETORNO.
9. Se genera un remito de retorno hacia la sede de pertenencia.
10. Cuando ese remito es recibido, el ejemplar vuelve a su sede de pertenencia y queda DISPONIBLE.

## Persistencia

Se utiliza SQLite.

Tablas principales:

- sedes
- socios
- libros
- ejemplares
- prestamos
- reservas
- remitos
- remito_ejemplares
- historial_remito

Las operaciones que modifican varias tablas se realizan con commit/rollback para evitar que una operación quede guardada parcialmente.

## Patrones de diseño

### Observer

Remito funciona como Subject. Cuando cambia correctamente de estado, notifica a sus observadores.

HistorialRemitoObserver recibe esa notificación y agrega el nuevo estado a historial_remito. De esta forma la trazabilidad queda separada de la lógica propia del Remito.

### Singleton

DatabaseSingleton centraliza el acceso a SQLite y mantiene una única instancia para administrar la conexión utilizada por la aplicación.

## Reportes

El sistema implementa cinco reportes:

1. préstamos activos y material en tránsito;
2. libros más solicitados para préstamos entre sedes;
3. disponibilidad de catálogo por sede;
4. movimientos entre sedes y tiempo promedio de tránsito;
5. préstamos vencidos.

Los primeros cuatro cubren el mínimo de cuatro reportes no triviales pedido por la consigna. El reporte de préstamos vencidos permite además controlar las fechas de vencimiento.

No se calcula una multa automática porque la consigna no define una regla ni un monto para hacerlo.

## Organización del proyecto

```
modelos/
datos/
patrones/
interfaz/
tests/
docs/
main.py
```

La interfaz se encarga de la interacción con el usuario. Las validaciones y reglas de negocio importantes también se controlan en la lógica del sistema.
