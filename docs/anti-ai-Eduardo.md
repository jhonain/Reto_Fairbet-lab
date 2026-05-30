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
---

### 2026-05-28 — Corrección de validación DNI en KYC simulado (Eduardo Puicon Paico)

| Fecha | Parte del proyecto | Tipo de uso | Detalle |
|-------|-------------------|-------------|---------|
| 2026-05-28 | `apps/users/validators.py` | Revisar validación KYC | ChatGPT/Codex se usó como apoyo para identificar que la validación anterior podía rechazar DNI reales al interpretar incorrectamente el último dígito. Yo adapté la validación para aceptar 8 dígitos numéricos y mantener el bloqueo de letras. |
| 2026-05-28 | `apps/users/tests.py` | Revisar cobertura | ChatGPT/Codex se usó como apoyo para actualizar las pruebas que dependían del dígito verificador y cubrir DNI válido, letras, longitud inválida, registro web, registro API y menor de edad. Yo validé que las pruebas reflejen la regla corregida. |
| 2026-05-28 | `templates/portal/registro.html` | Mejorar ayuda visual | ChatGPT/Codex se usó como apoyo para mantener restricciones visuales en el campo DNI. Yo validé que la seguridad principal siga en backend. |
| 2026-05-28 | `docs/adr/0007-validacion-dni-kyc-simulado.md` | Redactar decisión técnica | ChatGPT/Codex se usó como apoyo para estructurar el ADR según la plantilla del reto. Yo ajusté el contenido a la decisión realmente tomada. |

## Lo que hice yo en esta fase

* Probé el registro con un DNI real desde la interfaz.
* Detecté que la validación anterior generaba falsos negativos.
* Ajusté la regla para aceptar DNI de 8 dígitos numéricos.
* Revisé que el sistema siga rechazando letras y formatos inválidos.
* Ejecuté verificaciones del proyecto.
* Revisé que la documentación refleje solo lo implementado.
