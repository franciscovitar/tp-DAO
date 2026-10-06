# Diseño inicial - Tema 1

## Idea general

El sistema administra una red de bibliotecas con varias sedes. Cada sede tiene ejemplares físicos de libros y los socios pueden pedir préstamos locales o interbibliotecarios.

La idea es mantener el modelo simple y parecido a los ejercicios de la cátedra: clases con responsabilidades claras, lógica de negocio en los objetos y persistencia con SQLite sin agregar frameworks ni capas innecesarias.

## Clases principales

### Sede

Datos iniciales:
- id
- nombre
- dirección
- teléfono
- email
- horario
- activa

Responsabilidades:
- informar si la sede puede operar;
- mantener sus datos.

Una sede dada de baja no puede participar como origen ni destino de préstamos, reservas o envíos.

### Socio

Datos iniciales:
- id
- dni
- nombre
- apellido
- teléfono
- email
- habilitado

Responsabilidades:
- mantener sus datos;
- informar si puede solicitar préstamos.

El DNI debe ser único.

### Libro

Representa el dato de catálogo, no una copia física.

Datos iniciales:
- id
- isbn
- título
- autor
- editorial
- año

El ISBN se usa como identificador para evitar duplicados de catálogo.

### Ejemplar

Representa una copia física de un libro.

Datos iniciales:
- id
- código
- libro
- sede_pertenencia
- sede_actual
- estado
- estado_fisico

Estados operativos previstos:
- DISPONIBLE
- RESERVADO
- PRESTADO
- EN_TRANSITO
- BAJA

Estado físico inicial:
- BUENO
- DANADO

La sede de pertenencia no cambia por un préstamo interbibliotecario. La sede actual sí puede cambiar durante el traslado.

### Prestamo

Representa la solicitud y el préstamo de un ejemplar.

Datos iniciales:
- id
- socio
- ejemplar
- sede_origen
- sede_destino
- fecha_solicitud
- fecha_inicio
- fecha_vencimiento
- fecha_devolucion
- estado

Estados previstos:
- SOLICITADO
- ACTIVO
- DEVUELTO
- RECHAZADO
- CANCELADO

La condición de vencido se calcula comparando fecha_vencimiento con la fecha actual mientras el préstamo siga ACTIVO. No hace falta guardar VENCIDO como otro estado.

En una primera versión se puede trabajar con una clase Prestamo y distinguir local/interbibliotecario por origen y destino. Si al aplicar el segundo patrón conviene separar PrestamoLocal y PrestamoInterbibliotecario, se hará sin cambiar las reglas del negocio.

### Reserva

Datos iniciales:
- id
- socio
- ejemplar
- fecha
- estado

Estados previstos:
- ACTIVA
- CUMPLIDA
- CANCELADA

Una reserva activa impide que el ejemplar se preste a otro socio.

### Remito

Representa el traslado de uno o más ejemplares entre sedes.

Datos iniciales:
- id
- numero
- sede_origen
- sede_destino
- fecha_creacion
- fecha_despacho
- fecha_recepcion
- estado
- ejemplares

Estados iniciales:
- PREPARADO
- DESPACHADO
- EN_TRANSITO
- RECIBIDO

El cambio de estado debe quedar registrado en un historial. Ese historial no se modifica: cada cambio agrega un registro nuevo.

El ciclo de vida del remito es una parte importante del TP y se va a probar por separado.

## Relaciones principales

- una Sede tiene muchos Ejemplares;
- un Libro puede tener muchos Ejemplares;
- un Socio puede tener muchos Préstamos y Reservas;
- un Préstamo corresponde a un Socio y a un Ejemplar;
- un Remito tiene una sede origen, una sede destino y uno o más Ejemplares;
- cada cambio de estado de un Remito genera un registro en HistorialRemito.

## Reglas de negocio que hay que cubrir

1. No prestar un ejemplar que no esté disponible.
2. No prestar a un socio inhabilitado.
3. No iniciar operaciones desde o hacia una sede dada de baja.
4. El ejemplar tiene que pertenecer a la sede origen del préstamo.
5. Controlar la fecha de vencimiento del préstamo.
6. Evitar socios, libros y ejemplares duplicados por sus identificadores.
7. Mantener el historial completo de estados del remito.
8. La recepción de un remito actualiza la sede actual de los ejemplares.
9. Una devolución debe corresponder a un préstamo activo.
10. Al devolver se registra el estado físico del ejemplar.

## Persistencia

Se va a usar SQLite y consultas parametrizadas con ?, siguiendo el material de la materia.

Tablas previstas:

### sedes
- id PK
- nombre
- direccion
- telefono
- email
- horario
- activa

### socios
- id PK
- dni UNIQUE
- nombre
- apellido
- telefono
- email
- habilitado

### libros
- id PK
- isbn UNIQUE
- titulo
- autor
- editorial
- anio

### ejemplares
- id PK
- codigo UNIQUE
- libro_id FK
- sede_pertenencia_id FK
- sede_actual_id FK
- estado
- estado_fisico

### prestamos
- id PK
- socio_id FK
- ejemplar_id FK
- sede_origen_id FK
- sede_destino_id FK
- fecha_solicitud
- fecha_inicio
- fecha_vencimiento
- fecha_devolucion
- estado

### reservas
- id PK
- socio_id FK
- ejemplar_id FK
- fecha
- estado

### remitos
- id PK
- numero UNIQUE
- sede_origen_id FK
- sede_destino_id FK
- fecha_creacion
- fecha_despacho
- fecha_recepcion
- estado

### remito_ejemplares
- remito_id FK
- ejemplar_id FK

### historial_remito
- id PK
- remito_id FK
- estado
- fecha_hora

## Arquitectura propuesta

Se evita una arquitectura demasiado grande. La separación inicial sería:

```
modelos/
datos/
interfaz/
tests/
main.py
```

### modelos

Clases del dominio y reglas que corresponden a cada objeto.

### datos

Conexión SQLite y operaciones de persistencia.

No se usa ORM. Se trabaja con sqlite3, Connection, Cursor, execute, fetchone/fetchall, commit y rollback.

### interfaz

Formularios y pantallas. La tecnología concreta se define cuando quede confirmado el material oficial de interfaces de la cátedra.

La interfaz valida entradas, pero las reglas importantes también se validan en la lógica del sistema.

### tests

Pruebas con pytest para las reglas importantes y para el ciclo de estados.

## Patrones de diseño

La consigna pide por lo menos dos.

### 1. State - elegido

Se aplicará al ciclo de vida del Remito.

La razón es que el remito cambia de comportamiento según su estado y la consigna indica que su ciclo de vida será evaluado especialmente.

La transición debe ser controlada, por ejemplo:

PREPARADO -> DESPACHADO -> EN_TRANSITO -> RECIBIDO

No se permitirá saltar directamente de PREPARADO a RECIBIDO.

La implementación se hará con el nivel de complejidad visto en clase y se acompañará con pruebas.

### 2. Factory - candidato

Puede usarse para crear el tipo de préstamo correcto a partir de la sede origen y destino:
- préstamo local;
- préstamo interbibliotecario.

Antes de implementarlo se debe contrastar con el material de patrones de la cátedra. Si no coincide con lo enseñado, se reemplaza por otro patrón visto en clase.

No se va a agregar un patrón solamente para cumplir el número: tiene que resolver una necesidad real del modelo y poder defenderse.

## Reportes obligatorios elegidos

Se implementarán por lo menos estos cuatro:

1. Préstamos activos y material en tránsito.
2. Libros más solicitados para préstamos entre sedes.
3. Disponibilidad de catálogo por sede.
4. Movimientos de ejemplares entre sedes y tiempo promedio de tránsito.

Como reporte adicional puede agregarse préstamos vencidos.

No se calculan multas por ahora porque la consigna no define una regla para el monto.

## Pantallas previstas

1. Menú principal.
2. Sedes.
3. Socios.
4. Catálogo de libros.
5. Ejemplares.
6. Préstamos y solicitudes.
7. Reservas.
8. Remitos / logística.
9. Devoluciones.
10. Reportes.

## Punto que hay que confirmar

La consigna no explica en detalle qué ocurre con un ejemplar interbibliotecario después de que el socio lo devuelve en la sede destino.

La solución prevista es que el ejemplar vuelva a su sede de pertenencia mediante un nuevo remito, conservando toda la trazabilidad. Antes de cerrar ese flujo conviene validarlo con el profesor o con material específico de la entrega.
