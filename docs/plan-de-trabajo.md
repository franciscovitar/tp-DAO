# Plan de trabajo

El objetivo es construir el TP por partes y probar cada parte antes de seguir.

## Etapa 1 - Base del proyecto

- crear estructura de carpetas;
- crear clases Sede, Socio, Libro y Ejemplar;
- crear la base SQLite;
- crear tablas principales;
- probar altas, consultas y duplicados.

Resultado esperado: ABM básico del núcleo funcionando sin interfaz gráfica.

## Etapa 2 - Préstamo local

- crear Prestamo;
- validar socio habilitado;
- validar sede activa;
- validar ejemplar disponible;
- validar que el ejemplar pertenezca a la sede origen;
- registrar fecha de inicio y vencimiento;
- cambiar estado del ejemplar;
- registrar devolución.

Resultado esperado: flujo local completo probado con pytest.

## Etapa 3 - Reservas

- crear Reserva;
- registrar y cancelar reservas;
- impedir préstamos incompatibles;
- liberar/cumplir reserva al concretar el préstamo.

Resultado esperado: reservas consistentes con disponibilidad.

## Etapa 4 - Préstamo interbibliotecario y remitos

- crear Remito;
- asociar ejemplares;
- implementar estados;
- registrar historial de cada transición;
- despachar;
- marcar en tránsito;
- recibir;
- actualizar sede actual del ejemplar.

En esta etapa se incorpora el patrón State.

Resultado esperado: un ejemplar puede viajar de una sede a otra sin perder trazabilidad.

## Etapa 5 - Segundo patrón

- revisar el material de patrones que use la cátedra;
- confirmar Factory para préstamo local/interbibliotecario o reemplazarlo;
- implementarlo únicamente si simplifica una decisión real del sistema;
- agregar tests del patrón.

## Etapa 6 - Reportes

Implementar primero con SQL simple y funciones claras:

1. préstamos activos + ejemplares en tránsito;
2. libros más solicitados entre sedes;
3. disponibilidad por sede;
4. movimientos origen/destino + tiempo promedio de tránsito.

Resultado esperado: cuatro reportes no triviales con datos de prueba.

## Etapa 7 - Interfaz

Recién cuando el modelo y la persistencia estén estables:

- menú principal;
- ABM de sedes;
- ABM de socios;
- libros y ejemplares;
- préstamos;
- reservas;
- remitos;
- devoluciones;
- reportes.

No poner reglas importantes solamente en la pantalla. La interfaz debe llamar a la lógica ya probada.

## Etapa 8 - Pruebas finales

Probar especialmente:

- socio inhabilitado;
- sede dada de baja;
- ejemplar no disponible;
- duplicados;
- préstamo desde sede incorrecta;
- préstamo vencido;
- transición inválida de remito;
- devolución;
- estado físico del material;
- recepción y cambio de sede actual.

## Etapa 9 - Revisión de consigna

Leer nuevamente la consigna punto por punto y marcar cada requisito como:
- hecho;
- probado;
- visible en la interfaz;
- explicable en la defensa.

## Etapa 10 - Defensa

Preparar una explicación corta de:
- por qué existe cada clase;
- por qué Libro y Ejemplar son distintos;
- diferencia entre sede de pertenencia y sede actual;
- cómo se controla la disponibilidad;
- cómo funciona el ciclo del remito;
- por qué se eligieron los dos patrones;
- dónde se usan transacciones;
- qué pregunta responde cada reporte.

## Criterio de desarrollo

Prioridad:
1. consigna actual;
2. ejemplos y repositorio oficial 2026;
3. material 2026 de la materia;
4. ejemplos de clase;
5. conocimiento externo solamente si falta algo.

El código debe quedar simple, legible y defendible. No usar una técnica más compleja si con lo visto en clase se resuelve bien.
