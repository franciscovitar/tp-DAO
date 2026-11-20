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
- cancelación de solicitudes interbibliotecarias cuando el socio queda inhabilitado durante el traslado;
- validación de los datos ingresados (DNI, ISBN, año, email, teléfono, horario, dirección, días de préstamo entre 1 y 60, largo de los textos) y control de duplicados;
- remitos de ida y retorno con trazabilidad;
- consulta de disponibilidad;
- cinco reportes de gestión;
- patrones Observer y Singleton.

El flujo interbibliotecario mantiene la sede de pertenencia del ejemplar y registra su ubicación actual durante el traslado. Los remitos siguen el ciclo:

`PREPARADO -> DESPACHADO -> EN_TRANSITO -> RECIBIDO`

Si el socio queda inhabilitado mientras el ejemplar viaja, la solicitud puede cancelarse una vez recibido el ejemplar: el préstamo queda `CANCELADO` y el ejemplar vuelve a su sede con un remito de retorno.

Los días del préstamo se aplican al registrar un préstamo local o al **activar** una solicitud interbibliotecaria recibida. Los formularios se limpian después de guardar correctamente; si hay un error, conservan los datos para corregirlos. Las reglas de validación están en `datos/validaciones.py`.

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

La suite actual contiene 149 pruebas automatizadas (requiere `pip install pytest`).
