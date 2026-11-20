# TP Integrador DAO 2026

**Tema 1:** Biblioteca - Sistema de Préstamos Interbibliotecarios

Aplicación desarrollada en Python con SQLite y una interfaz gráfica en Tkinter/ttk.

## Funcionalidades

- administración de sedes y socios;
- catálogo de libros y ejemplares físicos;
- préstamos locales e interbibliotecarios;
- reservas y devoluciones;
- retiro de circulación de ejemplares devueltos dañados;
- bloqueo de la reactivación de ejemplares dañados hasta marcarlos como reparados;
- cancelación de solicitudes interbibliotecarias antes de activarlas (el socio desiste o queda inhabilitado);
- bloqueo de la baja de una sede mientras tenga préstamos entre sedes, remitos o devoluciones en curso;
- cancelación automática de las reservas activas de un socio al inhabilitarlo;
- validación de los datos ingresados (DNI, ISBN, año, email, teléfono, horario, dirección, días de préstamo entre 1 y 60, largo de los textos) y control de duplicados;
- remitos de ida y retorno con trazabilidad;
- consulta de disponibilidad;
- cinco reportes de gestión;
- patrones Observer y Singleton.

El flujo interbibliotecario mantiene la sede de pertenencia del ejemplar y registra su ubicación actual durante el traslado. Los remitos siguen el ciclo:

`PREPARADO -> DESPACHADO -> EN_TRANSITO -> RECIBIDO`

Una solicitud puede cancelarse mientras no esté activa. Si el ejemplar todavía no salió, vuelve a quedar `DISPONIBLE` y el remito preparado ya no puede despacharse. Si ya llegó a la sede destino, el préstamo queda `CANCELADO` y el ejemplar vuelve a su sede con un remito de retorno. Mientras viaja no se puede cancelar: hay que esperar a recibirlo.

Los días del préstamo se aplican al registrar un préstamo local o al **activar** una solicitud interbibliotecaria recibida. Los formularios se limpian después de guardar correctamente; si hay un error, conservan los datos para corregirlos. Las reglas de validación están en `datos/validaciones.py`.

Las direcciones pueden indicar una calle, camino o referencia sin número de altura (por ejemplo, `Av. Colón s/n`). Los DNI de 7 u 8 dígitos conservan los ceros iniciales. Los ISBN se admiten sin separadores o con todos sus componentes separados por guiones o espacios; se comprueba su formato, no la asignación oficial de cada segmento ni el dígito de control.

## Documentación

- `docs/diseno.md`: decisiones principales del modelo y funcionamiento.
- `docs/modelo.puml`: diagrama UML del dominio.
- `docs/der.puml`: modelo relacional.
- `docs/casos-uso.puml`: casos de uso.
- `docs/patrones.puml`: aplicación de Observer y Singleton.

## Estructura

```
modelos/
datos/
patrones/
interfaz/
tests/
docs/
main.py
```

## Ejecución

Requiere Python 3.10 o superior con Tkinter (incluido en el instalador de python.org). Ejecutar desde la carpeta raíz del proyecto, donde se crea `biblioteca.db`:

```bash
python main.py
```

## Pruebas

```bash
python -m pytest -q
```

La suite actual contiene 193 pruebas automatizadas (requiere `pip install pytest`).
