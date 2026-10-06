# Diseño inicial - Tema 1

## Criterio general

El TP se resuelve al nivel de la cátedra: clases simples, responsabilidades claras, SQLite, validaciones de negocio y patrones vistos en 2026. No se agregan capas o técnicas porque sí.

## Modelo principal

- Sede: contacto, horarios y estado activa/baja.
- Socio: datos e inhabilitación/habilitación.
- Libro: catálogo.
- Ejemplar: copia física, sede de pertenencia, sede actual, estado y estado físico.
- Prestamo: local o interbibliotecario.
- Reserva: reserva de ejemplar.
- Remito: traslado entre sedes.
- HistorialRemito: trazabilidad append-only.

Libro y Ejemplar son conceptos distintos. Un Libro puede tener varios Ejemplares.

En Ejemplar:
- sede_pertenencia no cambia por un préstamo interbibliotecario;
- sede_actual representa dónde se encuentra físicamente.

## Estados

Ejemplar:
- DISPONIBLE
- RESERVADO
- PRESTADO
- EN_TRANSITO
- BAJA

Prestamo:
- SOLICITADO
- ACTIVO
- DEVUELTO
- RECHAZADO
- CANCELADO

Reserva:
- ACTIVA
- CUMPLIDA
- CANCELADA

Remito:
- PREPARADO
- DESPACHADO
- EN_TRANSITO
- RECIBIDO

El remito sólo avanza en ese orden. Cada cambio agrega un registro en historial_remito y no modifica los anteriores.

## Flujo interbibliotecario

1. El socio solicita un ejemplar disponible de otra sede.
2. El Prestamo queda SOLICITADO y el ejemplar RESERVADO.
3. Se crea un Remito PREPARADO.
4. Al DESPACHAR, el ejemplar pasa a EN_TRANSITO.
5. El remito pasa por EN_TRANSITO.
6. Al RECIBIR, se actualiza sede_actual y el ejemplar queda RESERVADO para el socio.
7. Recién entonces se activa el préstamo y el ejemplar pasa a PRESTADO.
8. Cuando el socio devuelve el material, el préstamo queda DEVUELTO.
9. Si el ejemplar pertenece a otra sede, se genera un remito de retorno.
10. Al recibir el retorno, sede_actual vuelve a sede_pertenencia y el ejemplar queda DISPONIBLE.

## Persistencia

SQLite sin ORM.

Tablas:
- sedes
- socios
- libros
- ejemplares
- prestamos
- reservas
- remitos
- remito_ejemplares
- historial_remito

Las operaciones que modifican varias tablas usan commit/rollback.

## Patrones de diseño

El material 2026 recibido de la cátedra enseña Singleton, Factory y Observer.

### Observer - elegido e implementado

Remito funciona como Subject. Los observadores se registran con attach() y reciben update() cuando el remito cambia correctamente de estado.

HistorialRemitoObserver es el observador concreto utilizado por la aplicación: cuando recibe una actualización agrega el nuevo estado a historial_remito usando la misma transacción de la operación.

Así el patrón participa en una necesidad real del sistema: la trazabilidad del remito.

### Singleton - elegido e implementado

DatabaseSingleton centraliza el acceso a SQLite siguiendo el ejemplo de Singleton de base de datos entregado por la cátedra.

### Factory - alternativa

Factory está enseñado, pero no se agrega si no aparece una necesidad real de creación de objetos concretos.

### State - descartado

No se usa State porque no aparece entre los patrones enseñados en el material 2026 recibido. El control de transiciones del remito se resuelve con lógica simple del propio Remito.

## Reportes

1. Préstamos activos y material en tránsito.
2. Libros más solicitados entre sedes.
3. Disponibilidad de catálogo por sede.
4. Movimientos entre sedes y tiempo promedio de tránsito.
5. Préstamos vencidos.

Los primeros cuatro cubren el mínimo obligatorio. El quinto hace visible el control de vencimientos.

No se define una regla de multas porque la consigna no indica cómo calcular su monto.

## Arquitectura

```
modelos/
datos/
patrones/
interfaz/
tests/
docs/
main.py
```

Las reglas importantes permanecen fuera de la interfaz. La pantalla valida datos de entrada y llama a la lógica ya implementada.
