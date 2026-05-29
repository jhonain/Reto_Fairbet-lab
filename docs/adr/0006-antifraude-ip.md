# ADR 0006: Anti-fraude basico por IP

## Contexto

El reto pide anti-fraude basico y una de las reglas propuestas es detectar multiples cuentas desde la misma IP. El proyecto aun no tiene un sistema completo de fraude, por eso se implementa una primera version simple basada en alertas revisables por el administrador.

En esta fase solo se implementa la regla de multiples cuentas registradas desde una misma IP. No se implementan patrones de apuestas ni cash-out sospechoso.

## Opciones consideradas

Opcion 1: Bloquear automaticamente registros desde la misma IP.

Pros:

* Reduce abuso de multiples cuentas.
* Es una accion fuerte.

Contras:

* Puede generar falsos positivos en redes compartidas, como universidad, casa o cabina.
* Puede bloquear usuarios legitimos.
* Es demasiado agresivo para una primera version academica.

Opcion 2: Crear alertas SuspiciousActivity para revision manual.

Pros:

* Evita bloquear usuarios legitimos automaticamente.
* Cumple mejor como anti-fraude basico.
* Permite revision manual del administrador.
* Es simple y defendible.

Contras:

* Requiere que un administrador revise las alertas.
* No detiene automaticamente el comportamiento sospechoso.

## Decision

Se eligio crear alertas `SuspiciousActivity` para revision manual cuando se detecten multiples cuentas asociadas a una misma IP.

## Consecuencias

Se vuelve mas facil:

* Tener una primera capa anti-fraude.
* Revisar casos sospechosos desde el admin.
* Evitar bloqueos injustos.

Se vuelve mas dificil:

* Hay que revisar alertas manualmente.
* La deteccion por IP puede tener falsos positivos.

Deuda tecnica:

* En una version futura se podrian agregar reglas por patrones de apuestas.
* En una version futura se podria registrar IP de forma mas estructurada.
* En una version futura se podria integrar con dashboard del operador.

## Fecha y autor

Fecha: 2026-05-28.
Autor: Eduardo Puicon Paico.
