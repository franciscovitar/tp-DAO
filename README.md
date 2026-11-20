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

## Datos de demostración (opcional)

Para mostrar el TP sin cargar todo manualmente, cerrá primero la aplicación y ejecutá:

```bash
python cargar_datos_demo.py
python main.py
```

La primera orden agrega **3 sedes, 8 socios, 10 libros, 20 ejemplares,
3 reservas, 5 préstamos y 2 remitos**, todos ficticios. Incluye una reserva
activa, una cumplida, una cancelada, préstamos locales e interbibliotecarios,
un **préstamo activo vencido hace 7 días** ("1984", socio Nicolás Herrera),
un remito `PREPARADO`, otro `RECIBIDO` con historial y un **tiempo ficticio
de tránsito de 4 h 30 min** (visible en Reportes), y un ejemplar `BAJA/DANADO`
para practicar las validaciones.

Es una carga **manual y opcional**: `main.py` nunca la ejecuta por su cuenta.
No borra datos anteriores, no reemplaza registros existentes y evita duplicar
los ejemplos si se vuelve a ejecutar. Si ya habías cargado una versión anterior,
al volver a ejecutar el comando se añade el préstamo vencido **sólo si** el
ejemplar ficticio `DEMO-C-06` está disponible y nunca fue prestado ni reservado.
Los demás movimientos se crean sólo sobre ejemplares nuevos.

También se puede elegir otro archivo con `python cargar_datos_demo.py --bd prueba.db`.
El archivo `biblioteca.db` es local y está excluido de GitHub (`.gitignore`);
lo compartido en el repositorio es el script para generar los datos.

Si ya habías cargado la demostración con una versión anterior, el reporte
podría mostrar `0.00 h` porque el remito se despachó y recibió al instante.
Para corregir **sólo ese remito ficticio**, cerrá la aplicación y ejecutá
en la terminal de PowerShell, después de actualizar el código:

```powershell
Copy-Item .\biblioteca.db ".\biblioteca_backup_$(Get-Date -Format yyyyMMdd_HHmmss).db"
python cargar_datos_demo.py --ajustar-traslado-demo
python main.py
```

El comando normal no altera préstamos existentes; al actualizar una demostración
antigua puede sumar el caso vencido sobre el ejemplar ficticio sin uso. La opción
`--ajustar-traslado-demo` únicamente corrige `DEMO-IDA-002` si mantiene los
estados y fechas originales sin duración. No toca remitos reales ni otros
ejemplos. Si el remito ya tiene un tiempo registrado o fue modificado, lo deja
igual. La copia de seguridad permite recuperar la base anterior si hiciera falta.

## Pruebas

```bash
python -m pytest -q
```

La suite incluye pruebas automatizadas (requiere `pip install pytest`).
