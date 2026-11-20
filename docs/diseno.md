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

El historial de cada remito se almacena en la tabla `historial_remito` mediante
`HistorialRemitoObserver`. No se necesita una clase de dominio separada para
representar cada registro de historial.

Un Libro puede tener cero o varios Ejemplares. La sede de pertenencia indica a qué biblioteca pertenece la copia; la sede actual indica dónde se encuentra físicamente en cada momento.

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
- CANCELADO (solicitud interbibliotecaria cancelada antes de activarse)

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
10. Cuando ese remito es recibido, el ejemplar vuelve a su sede de pertenencia y queda DISPONIBLE si se devolvió en buen estado, o de BAJA si está dañado.

Si una devolución registra el estado físico `DANADO`, el ejemplar no vuelve
automáticamente a circulación: queda de `BAJA` al finalizar una devolución
local o al recibirse el remito de retorno interbibliotecario. Puede ser
reactivado por el personal de biblioteca con el botón «Marcar como reparado»,
que pasa su estado físico a `BUENO` y lo deja `DISPONIBLE`.

La cantidad de días se aplica al registrar un préstamo local o al activar
un préstamo interbibliotecario recibido. No queda fijada en la solicitud
inicial: al activar, el personal confirma el valor del campo «Días».

Antes de activar un préstamo interbibliotecario se comprueba nuevamente que
el socio siga habilitado y que no tenga préstamos vencidos, ya que su
condición puede cambiar durante el traslado del ejemplar.

Una solicitud puede cancelarse mientras siga `SOLICITADO`. Si el ejemplar
no salió de su sede vuelve a `DISPONIBLE` y su remito preparado ya no se
puede despachar; si ya llegó a la sede destino queda `PENDIENTE_RETORNO`
para el remito de retorno. Mientras viaja no se puede cancelar.

Una sede no puede darse de baja mientras participe de una solicitud o un
préstamo entre sedes sin terminar, de un remito despachado o en tránsito, o
tenga ejemplares propios o ajenos pendientes de retorno. Así ningún
ejemplar queda varado en una sede cerrada.

Al inhabilitar a un socio se cancelan sus reservas activas y los ejemplares
vuelven a estar disponibles. Las reservas no tienen vencimiento automático
porque la consigna no define un plazo.
También se verifica que las sedes origen y destino sigan activas al iniciar
el préstamo. Antes de despachar cualquier remito se vuelven a verificar
ambas sedes, ya que pueden haberse dado de baja desde la preparación.

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

## Validación de entradas

Las direcciones no exigen una altura numérica porque hay sedes ubicadas en caminos, campus o calles sin número. Se controla que contengan texto y caracteres admitidos, pero no se pretende verificar su existencia geográfica.

Los ISBN pueden ingresarse sin separadores o con sus componentes completos separados mediante guiones o espacios. La validación impide separadores mal ubicados y comprueba la longitud del identificador. No valida los rangos oficiales de registro/editor ni el dígito de control, ya que los ISBN de prueba no necesariamente son reales.

El DNI se guarda como texto y conserva el cero inicial cuando tiene 7 u 8 dígitos. Si se introduce un relleno adicional que supera los 8 dígitos, se elimina ese relleno antes de validar la longitud.

## Patrones de diseño

### Observer

Remito funciona como Subject. Cuando cambia correctamente de estado, notifica a sus observadores.

HistorialRemitoObserver recibe esa notificación y agrega el nuevo estado a historial_remito. De esta forma la trazabilidad queda separada de la lógica propia del Remito. El estado inicial PREPARADO también se registra a través del observador.

La notificación se hace después de escribir el cambio en la base y dentro de la misma transacción: si algo falla, se revierte todo y los observadores no reciben un estado que no se guardó.

### Singleton

DatabaseSingleton centraliza el acceso a SQLite: `__new__` crea el objeto la primera vez, lo guarda en `_instance` y en las llamadas siguientes devuelve ese mismo objeto. La instancia mantiene **una única conexión abierta** que comparten todas las operaciones de `datos/` (se obtiene con `conectar()`); las funciones no cierran la conexión, sólo hacen `commit` o `rollback`. La conexión se cierra una sola vez, al salir de la aplicación (`main.py`).

Si una operación terminara sin `commit`, la siguiente llamada a `conectar()` descarta esos cambios con `rollback`, para que no se confirmen por accidente junto con otra operación. Si la conexión fue cerrada, la instancia la vuelve a abrir al pedirla. Recibe el nombre del archivo para que las pruebas usen una base propia; `tests/conftest.py` cierra la conexión después de cada prueba.

## Reportes

El sistema implementa cinco reportes:

1. préstamos activos y material en tránsito;
2. libros más solicitados para préstamos entre sedes;
3. disponibilidad de catálogo por sede (sólo sedes activas);
4. movimientos entre sedes (remitos ya despachados) y tiempo promedio de tránsito;
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
