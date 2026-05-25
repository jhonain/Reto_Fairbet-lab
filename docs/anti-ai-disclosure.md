# Declaración de Uso de IA 

**Fecha:** 2026-05-24
**Autor:** Reynaldo Jhonain Vasquez Carrero
---

## Uso registrado

| Fecha | Parte del proyecto | Tipo de uso | Detalle |
|-------|-------------------|-------------|---------|
| 2026-05-24 | Estructura del proyecto (`apps/`, `config/`, `docs/`) | Generar boilerplate | Kimi sugirió organización de carpetas. Yo adapté: mantuve `events` como app separada, agregué `responsible_gaming` y `audit` según la guía. |
| 2026-05-24 | `docker-compose.yml` | Generar boilerplate | Configuración base sugerida por Kimi. Yo ajusté versiones (Postgres 16, Redis 7) y agregué healthchecks. |
| 2026-05-24 | Modelos `events` (`Evento`, `Mercado`, `Cuota`) | Revisar código | Mostré mi código a Kimi. Evalué sugerencias: agregué `momento_critico` e `es_ganadora` para in-play y liquidación. Rechacé agregar margen a nivel de cuota (pertenece a `Mercado`). |
| 2026-05-24 | Modelos `users` (`PerfilUsuario`, `AutoExclusion`, `LimiteDeposito`) | Revisar código | Kimi corrigió que `AutoExclusion` y `LimiteDeposito` deben apuntar a `Usuario`, no a `PerfilUsuario`. Yo implementé la separación KYC vs. juego responsable. |
| 2026-05-24 | Modelos `wallet` (`Cuenta`, `AsientoContable`, `ServicioBilletera`) | Revisar código | Kimi sugirió nombres en español y estructura de partida doble. Yo diseñé la lógica de liquidación (ganancia/pérdida) con 4 y 2 asientos respectivamente. |

---

## Lo que hice yo (sin IA)

- **Diseño de la máquina de estados de apuesta**: La esquematizaré en `docs/sketches/` antes de implementar.
- **Decisión de separar `events` de `betting`**: Basado en que el catálogo es dominio de lectura, independiente de transacciones.
- **Validaciones de negocio**: Límites de depósito con cooldown 24h, autoexclusión no reversible por el usuario.

---

### 2026-05-25 — Implementación de modelos faltantes (Nivel 1)

| Fecha | Parte del proyecto | Tipo de uso | Detalle |
|-------|-------------------|-------------|---------|
| 2026-05-25 | `apps/events/models.py` (Evento, Mercado, Cuota, HistorialCuota) y `apps/events/choices.py` | Revisar código | Copilot analizó la estructura existente de `users` y `wallet`, revisó que los nuevos modelos de eventos siguieran el mismo patrón (UUID, Decimal, choices). Sugirió agregar campos para in-play y auditoría. Yo los adapté e implementé. |
| 2026-05-25 | `apps/betting/models.py` (Apuesta, PiernaApuesta) y `apps/betting/choices.py` | Revisar código | Copilot revisó la implementación de los modelos de apuesta, verificó que los tipos de datos y relaciones fueran consistentes con `wallet` y `events`. Se validó el diseño pensando en apuestas combinadas y cash-out futuro. |
| 2026-05-25 | Análisis del PDF "Code Challenge - Casa de Apuestas.pdf" | Analizar requisitos | Copilot ayudó a desglosar el PDF en los 3 niveles funcionales y explicar qué cubría el proyecto actual. |
| 2026-05-25 | Documentación `docs/anti-ai-disclosure.md` | Redactar declaración | Copilot ayudó a redactar y mantener esta bitácora de uso de IA. |

---

## Commits con `[ai-assisted]`

| Hash | Mensaje |
|------|---------|
| *(pendiente)* | `chore: estructura inicial del proyecto [ai-assisted]` |
| *(pendiente)* | `feat(events): agregar modelo Evento con estados [ai-assisted]` |
| *(pendiente)* | `feat(users): implementar PerfilUsuario, AutoExclusion y LimiteDeposito [ai-assisted]` |
| *(pendiente)* | `feat(wallet): crear Cuenta y AsientoContable con partida doble [ai-assisted]` |

---
