# ADR 0007: Apuestas combinadas — validación y producto de cuotas

## Contexto

Las apuestas combinadas permiten agrupar múltiples selecciones en una sola apuesta. La cuota total es el producto de todas las cuotas individuales. La ganancia potencial crece rápido, pero todas las selecciones deben acertar para ganar.

La pregunta principal fue: ¿qué combinaciones de selecciones se permiten? ¿Se puede elegir Local y Empate del mismo evento? ¿Dos cuotas del mismo mercado?

## Opciones consideradas

### Opción 1: Solo una cuota por evento

Pros: simple, evita conflictos internos (ej. Local y Empate no pueden ganar ambas).
Contras: muy restrictivo; no permite combinar mercados distintos del mismo evento (ej. Local 1X2 + Over 2.5).

### Opción 2: Una cuota por combinación única de (evento, mercado)

Pros: permite Local + Over 2.5 del mismo evento, pero bloquea Local + Empate (mismo mercado 1X2).
Contras: la validación es ligeramente más compleja.

### Opción 3: Sin restricción

Pros: máxima libertad.
Contras: el usuario puede apostar combinaciones imposibles (Local y Empate) que serialmente no tienen valor.

## Decisión

Se eligió la Opción 2: validar usando tupla `(evento.id, mercado.id)` para evitar duplicados dentro del mismo mercado de un evento, permitiendo combinaciones de distintos mercados del mismo evento.

Cada selección también puede tener su propia `cuota_aceptada` para re-cotización individual.

La cuota total se calcula como producto de todas las `cuota_real` de las piernas.

## Consecuencias

Se vuelve más fácil:

- Combinar mercados distintos del mismo evento (ej. resultado + goles).
- Bloquear combinaciones redundantes del mismo mercado.

Se vuelve más difícil:

- La validación en el frontend también debe verificar la misma regla para dar feedback inmediato al usuario.

Deuda técnica:

- No se valida que las combinaciones sean lógicamente consistentes (ej. Local + Over 0.5 es válido aunque trivial).
- El operador no puede configurar qué mercados se pueden combinar.

## Fecha y autor

Fecha: 2026-05-29.
Autor: Grupo FairBet Lab.
