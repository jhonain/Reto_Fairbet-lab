# ADR 0005: Mensaje obligatorio de consumo responsable

## Contexto

El reto exige que el usuario vea y acepte un mensaje de juego responsable antes de confirmar cualquier apuesta. El mensaje debe ser visible en la interfaz y el usuario debe marcarlo explícitamente.

La pregunta es: ¿dónde se almacena el mensaje, cómo se forza su aceptación y dónde se muestra?

## Opciones consideradas

### Opción 1: Mensaje hardcodeado en el template HTML

Pros: simple, visible inmediatamente.
Contras: si cambia el texto, hay que buscar en cada template; no hay control backend de que el usuario realmente lo aceptó.

### Opción 2: Constante en Python + validación backend + checkbox en frontend

Pros: el backend rechaza apuestas sin `acepto_juego_responsable=True`.
Contras: requiere coordinación frontend-backend.

## Decisión

Se eligió la Opción 2.

- `MENSAJE_CONSUMO_RESPONSABLE` definido en `apps/responsible_gaming/constants.py`.
- Toda creación de apuesta (`crear_apuesta_simple`, `crear_apuesta_combinada`) valida que `acepto_juego_responsable` sea `True`.
- El portal muestra el mensaje antes del botón de confirmación y el checkbox está pre-renderizado.
- El mensaje se incluye en la respuesta JSON de la API REST.

## Consecuencias

Se vuelve más fácil:

- Cambiar el mensaje en un solo lugar.
- Garantizar que ninguna apuesta se crea sin aceptación explícita.

Se vuelve más difícil:

- El frontend debe enviar `acepto_juego_responsable` como campo obligatorio.

Deuda técnica:

- No hay log de qué versión del mensaje aceptó el usuario.
- No hay registro de la IP o fecha exacta de aceptación por cada apuesta individual más allá del `fecha_aceptacion` de la apuesta.

## Fecha y autor

Fecha: 2026-05-29.
Autor: Grupo FairBet Lab.
