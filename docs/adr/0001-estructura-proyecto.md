# ADR 0001 — Estructura del proyecto en apps Django

**Fecha:** 2026-05-25  
**Autor:** Grupo FairBet Lab  

## Contexto

El reto exige wallet, apuestas, eventos, KYC y juego responsable. Hay que decidir si un solo app monolítico o varias apps.

## Opciones consideradas

1. **Una sola app `core`:** más rápido al inicio, pero mezcla dominios y dificulta tests por módulo.
2. **Varias apps por dominio:** más carpetas, pero cada integrante puede defender un módulo.

## Decisión

Separar en: `users`, `wallet`, `events`, `betting`, `responsible_gaming`, `portal` (interfaz web) y dejar `dashboard`/`realtime` para niveles 2–3.

## Consecuencias

- Más fácil ubicar código y hacer commits atómicos por feature.
- Más migraciones y `INSTALLED_APPS` que mantener.
- La API REST y el portal comparten servicios (`ServicioBilletera`, `crear_apuesta_simple`).
