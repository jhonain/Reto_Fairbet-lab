# ADR 0004: Bloqueo de recargas con autoexclusion vigente

## Contexto

El sistema ya tenia autoexclusion y limites de deposito, pero la validacion de recarga debia considerar tambien la autoexclusion vigente para reforzar juego responsable.

La recarga simulada ya pasa por `responsible_gaming.services.validar_limite_recarga` antes de ejecutarse. Por eso la regla de autoexclusion puede integrarse en el modulo de juego responsable sin modificar `wallet`.

## Opciones consideradas

Opcion 1: Validar autoexclusion directamente en wallet.

Pros:

* El bloqueo queda cerca de la operacion de recarga.
* Es facil ver donde ocurre la validacion.

Contras:

* Mezcla logica de juego responsable dentro de wallet.
* Aumenta dependencia del modulo de Antony.
* Duplica responsabilidad.

Opcion 2: Validar autoexclusion dentro de validar_limite_recarga en responsible_gaming.

Pros:

* Mantiene la regla dentro del modulo de juego responsable.
* Reutiliza la integracion existente porque wallet ya llama ese servicio.
* Evita modificar el modulo wallet.

Contras:

* El nombre validar_limite_recarga ahora cubre limite y autoexclusion.
* En el futuro podria renombrarse a una funcion mas general.

## Decision

Se eligio validar la autoexclusion vigente dentro de `responsible_gaming.services.validar_limite_recarga`, porque `wallet` ya usa ese servicio antes de recargar.

## Consecuencias

Se vuelve mas facil:

* Bloquear recargas cuando hay autoexclusion vigente sin tocar wallet.
* Mantener la regla dentro de juego responsable.
* Defender la integracion entre modulos.

Se vuelve mas dificil:

* El servicio de validacion de recarga ahora valida mas que solo limites.

Deuda tecnica:

* En una version futura se podria separar en una funcion mas general como `validar_recarga_responsable`.
* Tambien se podria coordinar con wallet para bloquear otras operaciones sensibles si el equipo lo define.

## Fecha y autor

Fecha: 2026-05-28.
Autor: Eduardo Puicon Paico.
