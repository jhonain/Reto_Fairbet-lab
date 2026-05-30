# Declaración de Uso de IA

**Fecha:** 2026-05-28  
**Autor:** Norvil  
---

## Uso registrado

| Fecha | Parte del proyecto | Tipo de uso | Detalle |
|-------|-------------------|-------------|---------|
| 2026-05-28 | `apps/events/models.py` | Implementar | Creación de `post_save` signal para detectar cambios en eventos. La IA ayudó a estructurar el envío del payload hacia `channel_layer`. |
| 2026-05-28 | `apps/realtime/consumers.py` | Generar e integrar | Implementación de `CuotasConsumer`. Comparé enfoques síncronos vs asíncronos para decidir la mejor estabilidad con Daphne. |
| 2026-05-28 | `templates/events/eventos.html` | Generar UI | Script JS para abrir el WebSocket, escuchar mensajes `estado_mercado` y manipular el DOM (botón rojo) sin recargar página. |
| 2026-05-28 | `config/settings.py` | Corregir | La IA detectó que el `TimeoutError` se debía a una mala configuración de la URI de Redis y la falta de Daphne en `INSTALLED_APPS`. |
| 2026-05-28 | `docker-compose.yml` | Ajustar infraestructura | Configuración de Redis con parámetros `--timeout 0` y `--tcp-keepalive 60` para estabilizar los túneles de comunicación. |

---

## Lo que hice yo (sin IA)

- **Análisis de causa raíz en DBeaver:** Identifiqué por mi cuenta la discrepancia de sincronización en la base de datos. Validé que el modelo en Django es `PerfilUsuario` mediante introspección en el shell para corregir errores de inserción de UUIDs.
- **Diseño de la lógica de suspensión:** Decidí que el bloqueo sea total (botón deshabilitado y color rojo) para asegurar el cumplimiento del negocio.
- **Validación de flujo:** Pruebas manuales en el Admin de Django para asegurar que el cambio de estado en la DB sea consistente antes de la emisión.

---

### 2026-05-28 — Implementación de Tiempo Real y Suspensión (Nivel 2)

| Fecha | Parte del proyecto | Tipo de uso | Detalle |
|-------|-------------------|-------------|---------|
| 2026-05-28 | Análisis de logs de Docker | Depurar | La IA ayudó a desglosar el error `redis.exceptions.TimeoutError` identificando que el servicio web requería el protocolo ASGI nativo. |
| 2026-05-28 | `config/asgi.py` y `routing.py` | Revisar código | Se verificó que el enrutamiento de protocolos separara correctamente el tráfico HTTP del tráfico de WebSockets (`ProtocolTypeRouter`). |
| 2026-05-28 | Documentación `docs/anti-ia-norvil.md` | Redactar declaración | Basada en el formato de los compañeros de equipo; adapté mi bitácora de soporte técnico de hoy. |

---

## Commits con `[ai-assisted]`

- `Evidencia Norvil: Configuración de infraestructura Channels, Redis y lógica de suspensión In-play [ai-assisted]`