# Plan de trabajo

## Etapa 1 - Base
Estado: terminada.

Sede, Socio, Libro, Ejemplar, SQLite, altas, consultas y duplicados.

## Etapa 2 - Préstamo local
Estado: terminada.

Validación de socio, sede, disponibilidad, pertenencia, vencimiento y devolución.

## Etapa 3 - Reservas
Estado: terminada.

Alta, cancelación y concreción por el socio que reservó.

## Etapa 4 - Interbibliotecario y remitos
Estado: implementada en primera versión.

- solicitud interbibliotecaria;
- remito asociado;
- PREPARADO -> DESPACHADO -> EN_TRANSITO -> RECIBIDO;
- historial inmutable;
- cambio de sede actual al recibir;
- activación del préstamo después de la recepción;
- Observer aplicado al monitoreo del remito.

Pendiente: validar con el profesor el flujo de retorno del ejemplar después de la devolución.

## Etapa 5 - Segundo patrón
Implementar Singleton para el acceso a SQLite siguiendo el ejemplo DatabaseSingleton de la cátedra.

Factory queda sólo como alternativa si aparece una necesidad real.

## Etapa 6 - Reportes

1. préstamos activos y material en tránsito;
2. libros más solicitados entre sedes;
3. disponibilidad por sede;
4. movimientos origen/destino y tiempo promedio de tránsito.

## Etapa 7 - Interfaz

Incorporarla cuando el modelo y la persistencia estén estables. Las reglas de negocio no deben quedar solamente en la pantalla.

## Etapa 8 - Pruebas finales

Casos prioritarios:
- socio inhabilitado;
- sede de baja;
- ejemplar no disponible;
- duplicados;
- sede origen incorrecta;
- préstamo vencido;
- transición inválida de remito;
- devolución y estado físico;
- recepción y cambio de sede actual.

## Etapa 9 - Auditoría de consigna

Revisar cada requisito como hecho, probado, visible en interfaz y explicable en defensa.

## Etapa 10 - Defensa

Poder explicar clases, relaciones, Libro vs Ejemplar, sede de pertenencia vs actual, estados del remito, Observer, Singleton, transacciones y reportes.

## Regla de desarrollo

No usar una técnica más compleja si lo visto en clase resuelve correctamente el problema.
