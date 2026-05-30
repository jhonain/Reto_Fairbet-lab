# ADR 0009: Apuestas en vivo (in-play) — aceptación de eventos activos

## Contexto

El reto pide explícitamente aceptar apuestas mientras el evento está en vivo. Sin embargo, la validación actual en `services.py` rechaza todo evento que no esté en estado `PROGRAMADO`. El modelo `Evento` sí tiene el estado `EN_VIVO` definido en `EstadoEvento`, y el sistema de Channels ya soporta la actualización de cuotas y suspensión de mercados en tiempo real, pero la validación de creación de apuestas bloquea su uso.

La pregunta es: ¿cómo habilitar apuestas en vivo de forma segura?

## Opciones consideradas

### Opción 1: Eliminar la restricción de estado y aceptar PROGRAMADO + EN_VIVO

Cambiar `evento.estado != EstadoEvento.PROGRAMADO` por `evento.estado not in (EstadoEvento.PROGRAMADO, EstadoEvento.EN_VIVO)`.

Pros: mínimo cambio, habilita la funcionalidad.
Contras: no hay lógica extra de control para eventos en vivo (suspensión automática ya existe vía Channels).

### Opción 2: Crear un flag `apuestas_en_vivo` en Evento

Desacoplar el estado de la disponibilidad de apuestas.

Pros: más control granular.
Contras: más campos, más migraciones, más complejidad.

## Decisión

Se eligió la Opción 1 por ser la más directa. La lógica de suspensión de mercados para eventos críticos (gol, tarjeta roja) ya está cubierta por la señal `Cuota.post_save` que envía actualizaciones vía Channels, y el operador puede suspender mercados manualmente desde el admin.

La re-cotización ya maneja cambios de cuota en tiempo real, así que un evento en vivo con cuotas dinámicas es funcionalmente igual a uno programado con cuotas cambiantes.

## Consecuencias

Se vuelve más fácil:

- Habilitar apuestas en vivo con un cambio mínimo.
- Reutilizar toda la infraestructura existente (re-cotización, Channels, validación de saldo/KYC).

Se vuelve más difícil:

- El operador debe monitorear y suspender mercados manualmente si hay eventos críticos.
- No hay suspensión automática por detección de gol o tarjeta roja.

Deuda técnica:

- En el futuro se podría agregar suspensión automática mediante un feed de datos en tiempo real.
- El historial de cambios de cuota durante el evento en vivo queda en `HistorialCuota` pero no hay un marcador de "cambio por evento crítico".
- No hay diferenciación de márgenes entre pre-partido y en vivo (algunas casas usan márgenes más altos en vivo).

## Fecha y autor

Fecha: 2026-05-29.
Autor: Grupo FairBet Lab.
