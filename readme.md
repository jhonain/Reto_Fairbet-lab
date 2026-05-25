# FairBet Lab

Plataforma educativa de apuestas deportivas con moneda virtual. Proyecto desarrollado como parte del taller de lenguajes de programación — USS.

---

## Stack tecnológico

- **Backend:** Django 6.0.5 + DRF
- **Base de datos:** PostgreSQL
- **Cache / Tiempo real:** Redis + Django Channels
- **Tareas asíncronas:** Celery
- **Contenedores:** Docker + Docker Compose

---

## Estructura del proyecto

```
FairBet_Lab/
├── apps/
│   ├── betting/         # Lógica de apuestas (Apuesta, PiernaApuesta)
│   ├── dashboard/       # Dashboard del operador (Nivel 3)
│   ├── events/          # Catálogo de eventos, mercados y cuotas
│   ├── realtime/        # Cuotas en tiempo real (Nivel 2)
│   ├── responsible_gaming/  # Controles de juego responsable
│   ├── users/           # Usuarios, KYC, autoexclusión, límites de depósito
│   └── wallet/          # Billetera con contabilidad de partida doble
├── config/              # Configuración de Django (settings, urls, wsgi)
├── docs/                # Documentación (ADR, bocetos, declaración IA)
└── scripts/             # Scripts auxiliares
```

---

## Estado actual — Nivel 1 (Núcleo obligatorio)

### ✅ Implementado

| Componente | Apps | Detalle |
|------------|------|---------|
| Registro y KYC simulado | `users` | `PerfilUsuario` con DNI, edad, estados KYC. Validaciones de mayoría de edad. |
| Autoexclusión | `users` | `AutoExclusion` temporal (7/30/90 días) e indefinida. |
| Límites de depósito | `users` | `LimiteDeposito` diario/semanal/mensual con cooldown 24h para aumentos. |
| Wallet con partida doble | `wallet` | `Cuenta` y `AsientoContable` con débitos/créditos. `ServicioBilletera` con recarga y bloqueo de apuestas. Idempotencia y `select_for_update`. |
| Catálogo de eventos | `events` | `Evento` con estados, `Mercado` con tipos (1X2, Over/Under, BTTS, Hándicap), `Cuota` con historial inmutable. |
| Apuesta simple | `betting` | `Apuesta` con estados, `PiernaApuesta` para selecciones. Idempotencia, verificación de juego responsable. |

### 🔜 Pendiente (vistas/endpoints)

- Vistas de registro y verificación KYC
- Vistas de recarga/retiro/transferencia en wallet
- Vistas de listado de eventos y mercados
- Vista de creación y liquidación de apuestas
- Vistas de configuración de límites y autoexclusión

---

## Cómo ejecutar

```bash
docker-compose up --build
```

---

## Documentación

- `/docs/adr/` — Architectural Decision Records
- `/docs/sketches/` — Bocetos de ER y máquinas de estado
- `/docs/anti-ai-disclosure.md` — Declaración de uso de IA
