# Lecciones Aprendidas — FairBet Lab

## Principales dificultades técnicas

1. **Channels + Redis**: La integración de Django Channels con Redis fue el punto más problemático del proyecto. El `TimeoutError` constante al conectar con Redis en Docker requirió depurar configuración de timeouts (`--timeout 0`, `--tcp-keepalive 60`), asegurar Daphne como ASGI server, y verificar que `ProtocolTypeRouter` separara correctamente HTTP de WebSockets. Incluso en producción, las señales `post_save` de `Cuota` y `Mercado` necesitaron try/except para no romper el flujo si Redis no está disponible.

2. **Partida doble con `select_for_update`**: Implementar el saldo como suma de asientos (no campo almacenado) fue correcto conceptualmente, pero requirió asegurar que todas las transacciones usen `select_for_update` en el orden correcto para evitar deadlocks. Un error común fue olvidar bloquear la cuenta antes de crear asientos.

3. **Re-cotización en apuestas combinadas**: Coordinar la captura de `cuota_aceptada` por cada selección individual en el frontend y pasarla correctamente al backend fue más complejo de lo esperado. La solución fue almacenar el valor en `dataset.cuotaValor` del botón de cuota al hacer clic en el boleto.

4. **Validación de combinadas**: La decisión de usar `(evento_id, mercado_id)` como clave única en lugar de solo `evento_id` fue contra intuitiva al inicio, pero resultó necesaria para permitir Local + Over 2.5 del mismo evento. El equipo perdió tiempo inicialmente implementando la validación más restrictiva.

5. **Entorno híbrido SQLite/PostgreSQL**: Desarrollar en SQLite y desplegar en PostgreSQL generó diferencias sutiles: SQLite no soporta `CONCURRENTLY`, tiene comportamiento distinto con `Decimal` en agregaciones, y no permite probar `select_for_update` con `nowait=True` correctamente.

## Decisiones que generaron deuda técnica

1. **Cash-out sin vista portal**: Implementar cash-out solo como API REST fue rápido, pero obliga al usuario a consumir JSON en lugar de una interfaz amigable. La vista HTML quedó pendiente y requiere coordinación entre `portal/views.py` y el template.

2. **Sin Celery para tareas async**: La ausencia de Celery obligó a que operaciones como el cierre automático de mercados o el envío de reportes CSV sean manuales o se ejecuten de forma síncrona. Migrar a Celery implicaría refactorizar varias vistas.

3. **Cuotas con 4 decimales**: Implementar `decimal_places=4` en odds por consistencia con los campos monetarios fue una decisión temprana que no se alinea con el formato decimal europeo (ej. `2.50`). La migración a 2 decimales requiere cambiar el modelo y ajustar el cálculo de cuota total y re-cotización.

4. **Opción "local" genérica en lugar de "Perú"**: En el seed de eventos se usó "Local" y "Visitante" como nombres de equipo. Para un despliegue real se necesitarían nombres específicos y tal vez un modelo `Equipo`.

## Qué haríamos diferente

1. **Usar PostgreSQL desde el día 1**: Habría evitado las diferencias de comportamiento entre entornos y permitido probar `select_for_update` correctamente desde el inicio.

2. **Configurar Celery temprano**: Incluso sin tareas complejas, tener Celery disponible desde la semana 1 habría facilitado agregar tareas programadas sin refactorizar.

3. **Definir los ADRs antes de codificar**: Varias decisiones de diseño (re-cotización, validación de combinadas) se tomaron durante la implementación. Documentarlas como ADR primero habría ahorrado discusiones y retrabajo.

4. **Estandarizar el formato de cuotas (2 decimales) desde el principio**: El formato decimal europeo es el estándar de la industria. Usar 4 decimales por consistencia con montos fue un error de diseño.

## Consejos para próximos equipos

- Documenten la arquitectura antes de escribir código (ADRs, diagramas ER, máquinas de estado).
- Usen PostgreSQL local con Docker desde el inicio — SQLite es engañoso para sistemas transaccionales.
- Channels + Redis requiere configuración cuidadosa; no lo dejen para el final.
- Los tests de concurrencia (`select_for_update`) solo funcionan en PostgreSQL; planifiquen eso.
- La idempotencia (clave única) es su mejor defensa contra dobles envíos en el frontend.
