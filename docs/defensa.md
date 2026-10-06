# Guía corta para la defensa

## Idea general

El sistema administra una red de bibliotecas. Distingue el catálogo de las copias físicas, permite préstamos locales e interbibliotecarios y mantiene trazabilidad cuando un ejemplar se mueve entre sedes.

La decisión principal fue mantener el modelo simple y con responsabilidades separadas, usando SQLite y los patrones vistos en la materia.

## Decisiones que hay que poder explicar

### Libro y Ejemplar

Libro representa la información de catálogo: ISBN, título, autor, editorial y año.

Ejemplar representa una copia física concreta. Tiene su propio código, estado, estado físico y ubicación.

Esto permite tener un solo Libro y varias copias físicas del mismo título.

### Sede de pertenencia y sede actual

sede_pertenencia indica quién es el propietario del ejemplar.

sede_actual indica dónde se encuentra físicamente.

En un préstamo interbibliotecario la sede de pertenencia no cambia. La sede actual sí cambia cuando el remito es recibido.

### Préstamo local e interbibliotecario

El préstamo local se activa directamente si el socio, la sede y el ejemplar cumplen las validaciones.

El interbibliotecario primero queda SOLICITADO. El ejemplar viaja mediante un remito y el préstamo recién pasa a ACTIVO cuando el ejemplar fue recibido en la sede destino.

### Remito

El ciclo es:

PREPARADO -> DESPACHADO -> EN_TRANSITO -> RECIBIDO

No se permiten saltos de estado. Cada transición queda registrada en historial_remito.

Después de una devolución interbibliotecaria se usa otro remito para devolver el ejemplar a su sede de pertenencia.

## Patrones

### Observer

Remito es el Subject.

HistorialRemitoObserver es un Observer concreto. Cada vez que Remito cambia correctamente de estado, notify() llama a update() y el observador agrega el nuevo estado al historial.

Por qué sirve: Remito no necesita conocer cómo se persiste su historial. Solamente informa que cambió.

### Singleton

DatabaseSingleton mantiene una única instancia encargada del acceso a SQLite.

Por qué sirve: centraliza el recurso compartido de la base de datos y sigue el ejemplo de Singleton visto en clase.

### Por qué no Factory

Factory fue visto en clase, pero no apareció una necesidad real que justificara crear diferentes familias de objetos mediante fábricas. Agregarlo sólo para mostrar otro patrón hubiera hecho el diseño más complicado sin aportar al problema.

### Por qué no State

State no se eligió porque no forma parte de los patrones trabajados en el material 2026 recibido. Las transiciones del remito se controlan con una regla simple dentro de Remito.

## Transacciones

Se usan cuando una operación modifica varias tablas y los cambios deben quedar juntos.

Ejemplos:
- crear un préstamo y cambiar el estado del ejemplar;
- crear un remito, asociar el ejemplar y registrar PREPARADO;
- cambiar el estado de un remito, registrar el historial y actualizar el ejemplar;
- registrar una devolución.

Si ocurre un error, rollback evita que quede una parte de la operación guardada y otra no.

## Reportes

1. Préstamos activos y material en tránsito: permite saber qué material está actualmente comprometido.
2. Libros más solicitados entre sedes: ayuda a detectar títulos que convendría distribuir mejor.
3. Disponibilidad por sede: permite saber dónde hay ejemplares disponibles.
4. Movimientos y tiempo promedio de tránsito: permite evaluar la logística entre sedes.
5. Préstamos vencidos: hace visible el control de fechas de vencimiento.

No se calculan multas porque la consigna no define monto ni fórmula.

## Preguntas probables

### ¿Por qué el ejemplar queda RESERVADO cuando llega a destino?

Porque ya fue solicitado por un socio concreto. Si quedara DISPONIBLE, podría prestarse a otra persona antes de que el socio que lo pidió lo retire.

### ¿Por qué el préstamo no empieza cuando se genera la solicitud?

Porque todavía no tiene sentido cobrar días de préstamo mientras el ejemplar está viajando. La fecha de inicio y vencimiento se generan cuando el ejemplar ya llegó.

### ¿Por qué el historial del remito no se modifica?

Porque la consigna pide trazabilidad. Cada transición agrega un registro nuevo y conserva lo que ocurrió antes.

### ¿Qué pasa cuando se devuelve un ejemplar de otra sede?

El préstamo se cierra y luego se prepara un remito de retorno. Durante ese traslado el ejemplar no está disponible. Al llegar a su sede de pertenencia vuelve a DISPONIBLE.

### ¿Dónde están las reglas de negocio?

En la lógica de datos/modelo, no solamente en la interfaz. La pantalla valida entradas y muestra mensajes, pero no es la única barrera de consistencia.

### ¿Qué hace Singleton si una operación cerró la conexión?

La instancia sigue siendo la misma. Cuando se vuelve a pedir una conexión, DatabaseSingleton comprueba si está activa y la abre de nuevo si hace falta.

## Para mostrar en la presentación

Un recorrido corto y claro:

1. crear dos sedes;
2. crear socio, libro y ejemplar;
3. hacer una solicitud interbibliotecaria;
4. crear el remito y avanzar sus estados;
5. mostrar el historial;
6. activar el préstamo al recibir;
7. devolver;
8. generar el remito de retorno;
9. recibirlo en la sede de pertenencia;
10. mostrar disponibilidad y reportes.

Ese recorrido demuestra el núcleo diferencial del tema sin perder tiempo en ABM simples.
