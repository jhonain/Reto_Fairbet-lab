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

## Fase 5 — Límites de depósito con aumento pendiente

**Herramientas consultadas:** ChatGPT/Codex.

**Uso declarado:** Se utilizó IA como apoyo para analizar el requerimiento, comparar alternativas y revisar la organización de la solución. La IA no reemplazó la autoría del estudiante ni la comprensión del código.

**Partes donde se recibió apoyo:**

* `apps/responsible_gaming/models.py`: apoyo para revisar qué campos eran necesarios para representar un aumento pendiente de límite.
* `apps/responsible_gaming/views.py`: apoyo para organizar la respuesta del endpoint cuando un aumento queda pendiente.
* `apps/portal/views.py`: apoyo para ordenar el flujo de la pantalla de juego responsable.
* `templates/portal/responsable.html`: apoyo para estructurar la visualización del límite actual y del aumento pendiente.
* `docs/adr/0002-politica-limites-deposito.md`: apoyo para organizar el ADR según la plantilla solicitada.

**Participación del estudiante:** El código fue revisado, probado y adaptado antes de integrarse al repositorio. El estudiante validó el funcionamiento en la interfaz y revisó los cambios antes del commit.

**Partes que debo defender:**

* Diferencia entre bajar y subir límites.
* Uso de `monto_pendiente`.
* Uso de `pendiente_aplicable_desde`.
* Migración creada.
* Acción para aplicar el límite pendiente.
* Decisión registrada en el ADR.

---

### 2026-05-28 — Eduardo Puicon Paico — Usuarios y Juego Responsable

| Fecha | Parte del proyecto | Tipo de uso | Detalle |
|-------|-------------------|-------------|---------|
| 2026-05-28 | `apps/responsible_gaming/models.py` | Apoyo para revisar diseño | ChatGPT/Codex se usó como apoyo para analizar cómo representar un aumento pendiente de límite de depósito sin aplicarlo inmediatamente. Yo revisé la lógica antes de integrarla. |
| 2026-05-28 | `apps/responsible_gaming/views.py` | Apoyo para organizar respuesta | ChatGPT/Codex se usó como apoyo para organizar cómo informar al usuario que un aumento de límite quedó pendiente y cómo permitir aplicarlo cuando ya esté disponible. Yo validé que el flujo corresponda al requerimiento. |
| 2026-05-28 | `apps/responsible_gaming/admin.py` | Apoyo para revisar administración | ChatGPT/Codex se usó como apoyo para identificar qué campos de aumento pendiente debían ser visibles desde el panel administrativo. Yo revisé que solo se muestren datos relacionados con límites de depósito. |
| 2026-05-28 | `apps/responsible_gaming/migrations/0002_limite_deposito_aumento_pendiente.py` | Apoyo para organizar migración | ChatGPT/Codex se usó como apoyo para estructurar la migración de los nuevos campos de aumento pendiente. Yo revisé que la migración corresponda al modelo modificado. |
| 2026-05-28 | `apps/portal/views.py` | Apoyo para integrar cambios en interfaz web | ChatGPT/Codex se usó como apoyo para ordenar el flujo de la pantalla de juego responsable, mostrando aumentos pendientes y permitiendo aplicarlos cuando corresponda. Yo revisé que no se documente como implementado ningún bloqueo fuera de esta pantalla. |
| 2026-05-28 | `templates/portal/responsable.html` | Apoyo para reflejar cambios en la web | ChatGPT/Codex se usó como apoyo para mostrar en la interfaz el límite actual, el monto usado, el aumento pendiente y la fecha desde la cual puede aplicarse. Yo revisé que se refleje correctamente en pantalla. |
| 2026-05-28 | `docs/adr/0002-politica-limites-deposito.md` | Apoyo para documentación técnica | ChatGPT/Codex se usó como apoyo para estructurar el ADR según la plantilla solicitada por el reto. Yo adapté la decisión a lo realmente implementado en el proyecto. |

---

## Lo que hice yo — Eduardo Puicon Paico

* Revisé los cambios antes de integrarlos.
* Ejecuté los comandos de verificación del proyecto.
* Validé que los cambios correspondan a mi responsabilidad en `apps/users` y `apps/responsible_gaming`.
* Revisé que no se documente como implementado algo que no existe en el código.


---

### 2026-05-28 — Implementación de Users y Juego Responsable (Eduardo Puicon Paico)

| Fecha | Parte del proyecto | Tipo de uso | Detalle |
|-------|-------------------|-------------|---------|
| 2026-05-28 | `apps/users/serializers.py` | Revisar y organizar código | ChatGPT/Codex se usó como apoyo para revisar la validación del registro KYC mediante serializer. Yo adapté el flujo para validar DNI, mayoría de edad y datos obligatorios antes de crear el usuario. |
| 2026-05-28 | `apps/users/views.py` | Revisar flujo de registro API | ChatGPT/Codex se usó como apoyo para ordenar el flujo de registro por API y reducir duplicidad de validaciones. Yo verifiqué que el registro mantenga una respuesta clara y que no se creen usuarios inválidos. |
| 2026-05-28 | `apps/portal/views.py` | Integrar validación en interfaz web | ChatGPT/Codex se usó como apoyo para reutilizar la validación KYC en el registro web y para ordenar el flujo de límites en la pantalla de juego responsable. Yo adapté y revisé que no se documenten bloqueos fuera de lo implementado. |
| 2026-05-28 | `templates/portal/registro.html` | Mejorar interfaz de registro | ChatGPT/Codex se usó como apoyo para mejorar el campo DNI con restricciones visuales como longitud, patrón numérico y ayuda al usuario. Yo mantuve la validación principal en backend para que no dependa solo del HTML. |
| 2026-05-28 | `apps/users/services.py` | Organizar lógica de estado operativo | ChatGPT/Codex se usó como apoyo para estructurar una función simple que permita consultar si el usuario puede apostar y el motivo del bloqueo. Yo adapté esa lógica para usarla en el portal sin modificar el modelo. |
| 2026-05-28 | `templates/portal/perfil.html` y `templates/portal/eventos.html` | Reflejar estado operativo en la web | ChatGPT/Codex se usó como apoyo para ordenar la presentación del estado KYC, permiso para apostar y motivo de bloqueo. Yo validé que el usuario pueda ver esta información desde la interfaz. |
| 2026-05-28 | `apps/responsible_gaming/models.py` | Revisar diseño de límites de depósito | ChatGPT/Codex se usó como apoyo para comparar alternativas sobre el aumento de límites. Yo adapté la solución para que bajar el límite sea inmediato y subirlo quede pendiente hasta cumplir 24 horas. |
| 2026-05-28 | `apps/responsible_gaming/views.py` y `apps/portal/views.py` | Integrar flujo de límites | ChatGPT/Codex se usó como apoyo para organizar la respuesta cuando un aumento de límite queda pendiente y para reflejarlo en la pantalla de juego responsable. Yo revisé que el comportamiento corresponda al requerimiento. |
| 2026-05-28 | `apps/responsible_gaming/admin.py` | Revisar administración de límites | ChatGPT/Codex se usó como apoyo para identificar qué datos del aumento pendiente debían mostrarse en el panel administrativo. Yo revisé que la información sea útil para seguimiento sin agregar lógica innecesaria. |
| 2026-05-28 | `apps/responsible_gaming/migrations/0002_limite_deposito_aumento_pendiente.py` | Organizar migración | ChatGPT/Codex se usó como apoyo para estructurar la migración de los campos nuevos de aumento pendiente. Yo revisé que la migración corresponda al modelo realmente modificado. |
| 2026-05-28 | `templates/portal/responsable.html` | Mostrar límites y aumentos pendientes | ChatGPT/Codex se usó como apoyo para estructurar la visualización del límite actual, monto usado y aumento pendiente. Yo validé que la interfaz muestre la información necesaria para el usuario. |
| 2026-05-28 | `docs/adr/0002-politica-limites-deposito.md` | Redactar decisión técnica | ChatGPT/Codex se usó como apoyo para estructurar el ADR según la plantilla solicitada por el reto. Yo ajusté el contenido para que refleje únicamente la decisión implementada en mi módulo. |

---

## Lo que hice yo en mi módulo

* Adapté la validación de registro para que el DNI y la mayoría de edad se validen desde backend.
* Probé que el registro web no acepte DNI con letras.
* Ejecuté pruebas y verificaciones del proyecto antes de preparar commits.
* Revisé los cambios generados antes de integrarlos a mi rama.
* Validé que mi trabajo se mantenga dentro de `apps/users` y `apps/responsible_gaming`.
* Separé la explicación de estudio en PDF sin agregar comentarios innecesarios dentro del código fuente.
* Preparé la documentación técnica de mi decisión sobre límites de depósito mediante ADR.
* Revisé que no se documente como implementado algo que todavía no está en el código.

---

### 2026-05-28 — Autoexclusión vigente (Eduardo Puicon Paico)

| Fecha | Parte del proyecto | Tipo de uso | Detalle |
|-------|-------------------|-------------|---------|
| 2026-05-28 | `apps/responsible_gaming/models.py` | Revisar regla de vigencia | ChatGPT/Codex se usó como apoyo para ordenar la regla que determina si una autoexclusión está vigente. Yo adapté la lógica para diferenciar exclusiones indefinidas, temporales vigentes y temporales vencidas. |
| 2026-05-28 | `apps/responsible_gaming/services.py` | Organizar lógica reutilizable | ChatGPT/Codex se usó como apoyo para centralizar la consulta de autoexclusión vigente en un servicio simple. Yo revisé que pueda reutilizarse desde API y portal. |
| 2026-05-28 | `apps/responsible_gaming/views.py` | Revisar flujo API | ChatGPT/Codex se usó como apoyo para revisar que el endpoint consulte únicamente autoexclusiones vigentes. Yo validé que no se documente como activo algo vencido. |
| 2026-05-28 | `apps/portal/views.py` y `templates/portal/responsable.html` | Reflejar cambios en la web | ChatGPT/Codex se usó como apoyo para mostrar correctamente la autoexclusión vigente en la pantalla de juego responsable. Yo probé el comportamiento desde la interfaz. |
| 2026-05-28 | `docs/adr/0003-politica-autoexclusion.md` | Redactar decisión técnica | ChatGPT/Codex se usó como apoyo para estructurar el ADR según la plantilla del reto. Yo ajusté el contenido a lo realmente implementado. |

## Lo que hice yo en esta fase

* Revisé la diferencia entre autoexclusión activa y autoexclusión vigente.
* Validé que una autoexclusión vencida no se muestre como vigente.
* Revisé los cambios antes de integrarlos.
* Ejecuté verificaciones del proyecto.

---

### 2026-05-28 — Bloqueo de recargas con autoexclusión vigente (Eduardo Puicon Paico)

| Fecha | Parte del proyecto | Tipo de uso | Detalle |
|-------|-------------------|-------------|---------|
| 2026-05-28 | `apps/responsible_gaming/services.py` | Revisar regla de bloqueo | ChatGPT/Codex se usó como apoyo para ordenar la validación de recargas cuando existe una autoexclusión vigente. Yo adapté la lógica para reutilizar la consulta de autoexclusión vigente sin modificar wallet. |
| 2026-05-28 | `templates/portal/responsable.html` | Reflejar regla en la interfaz | ChatGPT/Codex se usó como apoyo para redactar un aviso claro sobre el bloqueo de recargas durante una autoexclusión vigente. Yo revisé que el texto corresponda a lo realmente implementado. |
| 2026-05-28 | `docs/adr/0004-bloqueo-recargas-autoexclusion.md` | Redactar decisión técnica | ChatGPT/Codex se usó como apoyo para estructurar el ADR según la plantilla del reto. Yo ajusté la decisión para que refleje únicamente lo implementado en esta fase. |

## Lo que hice yo en esta fase

* Revisé que wallet ya llama a validar_limite_recarga antes de recargar.
* Adapté la validación para que considere autoexclusión vigente.
* Validé que la regla pertenezca a responsible_gaming y no a wallet.
* Ejecuté verificaciones del proyecto.
* Revisé que no se documente como implementado algo que esta fase no toca.

---

### 2026-05-28 — Anti-fraude básico por IP (Eduardo Puicon Paico)

| Fecha | Parte del proyecto | Tipo de uso | Detalle |
|-------|-------------------|-------------|---------|
| 2026-05-28 | `apps/responsible_gaming/models.py` | Revisar diseño de alerta | ChatGPT/Codex se usó como apoyo para estructurar un modelo simple de alerta antifraude. Yo adapté el modelo para que sea revisable desde el admin y no bloquee automáticamente al usuario. |
| 2026-05-28 | `apps/responsible_gaming/services.py` | Organizar regla antifraude | ChatGPT/Codex se usó como apoyo para ordenar la regla de múltiples cuentas por IP. Yo mantuve la implementación básica y limitada a una primera versión. |
| 2026-05-28 | `apps/users/views.py` | Integrar evaluación tras registro | ChatGPT/Codex se usó como apoyo para ubicar el punto donde evaluar la IP después de crear un usuario. Yo revisé que la alerta no rompa el flujo de registro. |
| 2026-05-28 | `apps/responsible_gaming/admin.py` | Revisar visualización admin | ChatGPT/Codex se usó como apoyo para mostrar las alertas en el panel administrativo. Yo validé que sea útil para revisión manual. |
| 2026-05-28 | `apps/responsible_gaming/migrations/0003_suspiciousactivity.py` | Crear migración | ChatGPT/Codex se usó como apoyo para revisar que la migración corresponda al modelo de alerta implementado. Yo validé que no incluya reglas fuera de esta fase. |
| 2026-05-28 | `docs/adr/0006-antifraude-ip.md` | Redactar decisión técnica | ChatGPT/Codex se usó como apoyo para estructurar el ADR según la plantilla del reto. Yo ajusté el contenido a lo realmente implementado. |

## Lo que hice yo en esta fase

* Revisé la regla de múltiples cuentas desde una misma IP.
* Decidí usar alertas revisables en lugar de bloqueo automático.
* Validé que esta fase no implemente reglas no existentes como patrones de apuestas o cash-out.
* Ejecuté verificaciones del proyecto.
* Revisé que la documentación refleje solo lo implementado.

---

### 2026-05-28 — Mensaje obligatorio de consumo responsable (Eduardo Puicon Paico)

| Fecha | Parte del proyecto | Tipo de uso | Detalle |
|-------|-------------------|-------------|---------|
| 2026-05-28 | `apps/portal/views.py` | Revisar integración del mensaje | ChatGPT/Codex se usó como apoyo para revisar que el mensaje de consumo responsable se envíe al template desde la vista correspondiente. Yo validé que se use la constante existente y no texto duplicado. |
| 2026-05-28 | `templates/portal/eventos.html` | Mejorar visualización en interfaz | ChatGPT/Codex se usó como apoyo para ordenar la presentación del mensaje obligatorio antes de confirmar una apuesta. Yo revisé que el texto se vea en la pantalla real de eventos. |
| 2026-05-28 | `docs/adr/0005-mensaje-consumo-responsable.md` | Redactar decisión técnica | ChatGPT/Codex se usó como apoyo para estructurar el ADR según la plantilla del reto. Yo ajusté el contenido a lo realmente implementado. |

## Lo que hice yo en esta fase

* Revisé dónde se realiza la apuesta desde la interfaz.
* Validé que el mensaje obligatorio se tome desde la constante existente.
* Revisé que el mensaje sea visible antes de confirmar la apuesta.
* Ejecuté verificaciones del proyecto.

