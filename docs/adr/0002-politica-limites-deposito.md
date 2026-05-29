# ADR 0002: Política de límites de depósito

## Contexto

El reto exige que bajar un límite de depósito se aplique de forma inmediata y que subirlo espere 24 horas. El código anterior aplicaba el aumento inmediatamente y luego registraba un enfriamiento. Eso no cumple estrictamente la regla, porque el usuario obtenía el límite alto sin esperar.

## Opciones consideradas

Opción 1: Aplicar el aumento inmediatamente y bloquear otro aumento por 24 horas.

Pros:

* Más simple.
* Ya estaba parcialmente implementado.

Contras:

* No cumple estrictamente el reto.
* El usuario obtiene el límite alto sin esperar.

Opción 2: Guardar el aumento como pendiente y aplicarlo después de 24 horas.

Pros:

* Cumple mejor el reto.
* Es más seguro para juego responsable.
* Es fácil de explicar.

Contras:

* Requiere nuevos campos.
* Requiere una acción para aplicar el aumento cuando esté disponible.

## Decisión

Se eligió guardar el aumento como pendiente y aplicarlo después de 24 horas.

Para eso, `LimiteDeposito` guarda el monto actual en `monto` y el aumento solicitado en `monto_pendiente`. También registra desde cuándo está pendiente y desde cuándo se puede aplicar. Cuando ya pasaron las 24 horas, el usuario puede aplicar el aumento desde la pantalla de juego responsable.

## Consecuencias

Se vuelve más fácil:

* Cumplir la regla de juego responsable.
* Mostrar al usuario qué aumento está pendiente.
* Defender la decisión ante el profesor.

Se vuelve más difícil:

* Hay más campos en el modelo.
* Hay que controlar cuándo aplicar el aumento.

Deuda técnica:

* En una versión futura se podría aplicar automáticamente con Celery.
* Por ahora se aplica manualmente desde la pantalla de juego responsable o desde el flujo definido en esta fase.

## Fecha y autor

Fecha: 2026-05-28.
Autor: Eduardo Puicon Paico.
