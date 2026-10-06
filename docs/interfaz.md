# Decisión de interfaz

La materia indica que el proyecto integrador debe incluir interfaces gráficas, eventos, formularios y validaciones.

En las fuentes 2026 disponibles para este TP no se encontró una librería de interfaz obligatoria ni ejemplos oficiales que indiquen Tkinter, CustomTkinter u otro toolkit concreto.

Por eso se eligió Tkinter con ttk como decisión técnica mínima:
- viene con Python;
- no agrega dependencias;
- permite formularios, eventos, tablas y mensajes;
- mantiene el proyecto fácil de ejecutar y defender.

Esta elección es una inferencia de implementación, no una exigencia explícita de la consigna.

La primera versión usa un ttk.Notebook con pestañas para cada grupo de operaciones. Las reglas de negocio permanecen fuera de la interfaz.
