# Estado actual del TP

Actualizado: 2026-10-06

## Decisiones canónicas

- Tema: Biblioteca - Sistema de Préstamos Interbibliotecarios.
- Repositorio: franciscovitar/tp-DAO.
- Código en Python + SQLite.
- Mantener el nivel y estilo de la cátedra; evitar sobreingeniería.
- Patrones enseñados en el material 2026 recibido: Singleton, Factory y Observer.
- Patrones elegidos e implementados: Observer + Singleton.
- State descartado; Factory queda como alternativa.
- La cátedra exige interfaz gráfica, formularios y validaciones, pero en las fuentes disponibles no aparece prescripta una librería concreta. Se eligió Tkinter/ttk por ser parte de la biblioteca estándar de Python y no agregar dependencias externas.

## Implementado

- Sede, Socio, Libro, Ejemplar, Prestamo, Reserva y Remito.
- Préstamo local, devolución y reservas.
- Solicitud de préstamo interbibliotecario.
- Remito con PREPARADO -> DESPACHADO -> EN_TRANSITO -> RECIBIDO.
- Historial de remito append-only.
- Recepción con actualización de sede_actual.
- Activación del préstamo interbibliotecario luego de recibir.
- Observer para monitoreo de cambios del Remito.
- DatabaseSingleton para centralizar el acceso a SQLite.
- Cuatro reportes no triviales.
- Primera interfaz gráfica funcional con pestañas para:
  - sedes;
  - socios;
  - catálogo y ejemplares;
  - préstamos y devoluciones;
  - reservas;
  - remitos;
  - reportes.

## Interfaz

La pantalla permite altas y modificaciones básicas de sedes, socios y libros; alta de ejemplares; préstamo local e interbibliotecario; devolución; reserva/cancelación; preparación y avance del remito; consulta del historial; y visualización de los cuatro reportes.

Las reglas importantes siguen en la lógica/datos. La interfaz valida campos requeridos y formatos simples, pero no reemplaza las validaciones de negocio.

## Verificación

- El checkpoint anterior del núcleo tenía 26 tests registrados como aprobados.
- El nuevo bloque de interfaz fue validado por sintaxis con py_compile.
- Se verificó que tkinter puede importarse en el entorno disponible.
- Falta una ejecución visual completa de la interfaz en un entorno con escritorio y una regresión completa del proyecto después de este bloque.

## Pendiente inmediato

1. Ejecutar la interfaz visualmente y corregir detalles de uso si aparecen.
2. Resolver o validar el retorno del ejemplar a sede de pertenencia después de una devolución interbibliotecaria.
3. Auditar la consigna requisito por requisito.
4. Completar pruebas de regresión y casos límite.
5. Preparar defensa.

## Punto abierto

El retorno del ejemplar luego de una devolución interbibliotecaria no está definido expresamente en la consigna. No fijarlo como regla definitiva hasta validarlo con el profesor o material oficial.
