# Declaración de Uso de Herramientas de IA

**Integrante:** [Tu Nombre Completo]  
**Fecha de inicio del proyecto:** 2026-05-24  
**Última actualización:** [Actualizar al final de cada sprint]

---

## 1. Principio de uso

He utilizado herramientas de IA generativa (ChatGPT, Claude, Kimi, GitHub Copilot)
como **apoyo al aprendizaje y productividad**, nunca como sustituto de mi 
comprensión. Puedo explicar y modificar línea por línea todo el código que 
entrego, incluyendo el que recibió asistencia de IA.

---

## 2. Registro detallado por interacción

| Fecha | Parte del proyecto | Tipo de uso | Detalle específico | Mi contribución |
|-------|--------------------|-------------|-------------------|-----------------|
| 2026-05-24 | Estructura del proyecto (`fairbet-lab/`) | Generar boilerplate | Consulté a Kimi sobre organización de apps Django para un proyecto de apuestas. Me sugirió separar `wallet`, `betting`, `users`, `responsible_gaming`. | **Yo decidí** mantener `events` como app separada en lugar de fusionarla en `betting`, porque el catálogo de eventos es un dominio independiente. Adapté la estructura a las necesidades del reto. |
| 2026-05-24 | `docker-compose.yml` | Generar boilerplate | Kimi generó configuración base con Postgres, Redis, Celery. | **Yo ajusté** versiones (Postgres 16, Redis 7), agregué healthchecks, separé el servicio `channels` para WebSockets, y configuré dependencias condicionales (`condition: service_healthy`). |
| 2026-05-24 | Modelos `events` (`Event`, `Market`, `Odd`) | Revisar código | Mostré mi código actual a Kimi y pedí feedback sobre campos faltantes según la guía. | **Yo evalué** cada sugerencia: agregué `is_critical_moment` y `is_winning` porque son obligatorios para in-play y liquidación. **Rechacé** agregar un campo `profit_margin` a nivel de `Odd` porque el margen es del operador a nivel de `Market`, no por selección. |
| | | | | |
| | | | | |
| | | | | |

---

## 3. Categorías de uso (marcar con X)

| Categoría | ¿La usé? | Descripción breve |
|-----------|----------|-------------------|
| **Explicar concepto** | [ ] | La IA me explicó un tema que luego yo implementé |
| **Depurar error** | [ ] | La IA me ayudó a entender un traceback o bug |
| **Revisar código** | [X] | La IA revisó mi código y sugirió mejoras |
| **Generar boilerplate** | [X] | La IA generó código base que yo adapté |
| **Comparar enfoques** | [ ] | La IA comparó alternativas y yo decidí |
| **Ninguna de las anteriores** | [ ] | Este componente lo hice 100% yo |

---

## 4. Componentes SIN asistencia de IA (lo hice yo)

Estos son los componentes que diseñé, implementé y puedo defender **sin ayuda**:

- [ ] **Modelo `LedgerEntry` (partida doble):** Diseñé la estructura de débito/crédito basado en clases de contabilidad. La IA no vio mi implementación final.
- [ ] **Algoritmo de dígito verificador DNI peruano:** Implementé el módulo 11 con validaciones de longitud y casos de borde.
- [ ] **Máquina de estados de `Bet`:** La diseñé con diagrama en papel primero (ver `docs/sketches/maquina-estados-bet.jpg`).
- [ ] **Tests de concurrencia:** Escribí simulaciones con múltiples hilos para verificar `select_for_update`.
- [ ] **Controles de juego responsable:** Los diseñé leyendo la Ley 31557, no consultando IA.

*(Marcar a medida que avances el proyecto)*

---

## 5. Commits marcados con `[ai-assisted]`

| Hash | Fecha | Mensaje | Tipo de asistencia |
|------|-------|---------|-------------------|
| | | | |
| | | | |

*(Actualizar al final de cada sprint)*

---

## 6. Autoevaluación

En una escala del 1 al 10, mi nivel de transparencia es: **___/10**

**Justificación:** 

---

## 7. Declaración

Declaro que la información anterior es veraz. Entiendo que cualquier sección 
del código que no pueda explicar y modificar en vivo durante el walkthrough 
será considerada no entregada para fines de mi nota individual.

**Firma:** ___________________  
**Fecha:** ___________________