# ADR 0008: Cash-out — fórmula, margen y ejecución contable

## Contexto

El cash-out permite al usuario liquidar una apuesta aceptada antes de que termine el evento, obteniendo un monto calculado en base a las cuotas actuales. La pregunta fue: ¿qué fórmula usar y cómo registrarlo contablemente?

## Opciones consideradas

### Opción 1: Fórmula lineal sin margen

`cash_out = stake * cuota_original / cuota_actual`

Pros: simple, fácil de explicar.
Contras: la casa no tiene margen de ganancia en la operación.

### Opción 2: Fórmula con margen del 3%

`cash_out = stake * cuota_original / cuota_actual * (1 - 0.03)`

Pros: la casa retiene un pequeño margen.
Contras: el usuario recibe ligeramente menos.

### Opción 3: Cash-out fijo definido por operador

Pros: control total.
Contras: no escala, requiere intervención manual.

## Decisión

Se eligió la Opción 2 con margen del 3%.

Contablemente, `ServicioBilletera.ejecutar_cash_out` crea tres asientos:

1. Débito a APUESTAS_PENDIENTES (devuelve el stake bloqueado).
2. Crédito a BILLETERA_USUARIO (el monto cash-out).
3. Crédito a CASA (la diferencia: stake - cash-out = ganancia de la casa).

## Consecuencias

Se vuelve más fácil:

- Calcular el cash-out en una sola función reutilizable (`calcular_cash_out`).
- Ejecutar con transacción atómica.

Se vuelve más difícil:

- El margen del 3% puede ser alto para apuestas con cuotas muy bajas, resultando en cash-out cercano a cero.

Deuda técnica:

- El cash-out solo está disponible vía API REST; falta vista HTML en el portal.
- No se persiste el histórico de cálculos de cash-out (solo el monto final en `Apuesta.monto_cash_out`).
- No hay tope máximo de cash-out.

## Fecha y autor

Fecha: 2026-05-29.
Autor: Grupo FairBet Lab.
