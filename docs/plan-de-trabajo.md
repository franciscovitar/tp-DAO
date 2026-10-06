# Plan de trabajo

## Etapa 1 - Base
Estado: terminada.

## Etapa 2 - Préstamo local
Estado: terminada.

## Etapa 3 - Reservas
Estado: terminada.

## Etapa 4 - Interbibliotecario y remitos
Estado: implementada en primera versión.

Incluye solicitud, remito, trazabilidad, recepción y Observer.

Pendiente: validar el flujo de retorno después de una devolución interbibliotecaria.

## Etapa 5 - Patrones
Estado: terminada.

- Observer aplicado al monitoreo del Remito.
- Singleton aplicado al acceso a SQLite siguiendo el ejemplo DatabaseSingleton de la cátedra.
- Factory queda como alternativa si aparece una necesidad real.

## Etapa 6 - Reportes

Implementar:
1. préstamos activos y material en tránsito;
2. libros más solicitados entre sedes;
3. disponibilidad por sede;
4. movimientos origen/destino y tiempo promedio de tránsito.

## Etapa 7 - Interfaz

Agregarla cuando el modelo y la persistencia estén estables. Las reglas de negocio no deben quedar solamente en la pantalla.

## Etapa 8 - Pruebas finales

Cubrir reglas normales, límites y errores relevantes.

## Etapa 9 - Auditoría de consigna

Revisar cada requisito como hecho, probado, visible en interfaz y explicable en defensa.

## Etapa 10 - Defensa

Poder explicar clases, relaciones, Libro vs Ejemplar, sede de pertenencia vs actual, estados del remito, Observer, Singleton, transacciones y reportes.

## Regla de desarrollo

No usar una técnica más compleja si lo visto en clase resuelve correctamente el problema.
