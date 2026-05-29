# ADR 0003: Politica de autoexclusion vigente

## Contexto

El usuario puede tener registros historicos de autoexclusion, pero no todos deben bloquearlo. Una autoexclusion temporal vencida no debe tratarse como vigente.

La regla necesaria es distinguir entre una autoexclusion marcada como activa y una autoexclusion realmente vigente. Una autoexclusion vigente debe cumplir que `activa=True` y que `fecha_fin` sea nula para una exclusion indefinida, o que `fecha_fin` sea mayor a la fecha y hora actual para una exclusion temporal vigente.

## Opciones consideradas

Opcion 1: Consultar solo activa=True.

Pros:

* Es mas simple.
* Requiere menos logica.

Contras:

* Puede bloquear al usuario aunque la autoexclusion temporal ya haya vencido.
* No representa bien la regla de negocio.

Opcion 2: Calcular vigencia usando activa y fecha_fin.

Pros:

* Diferencia correctamente entre autoexclusion vigente y vencida.
* Respeta mejor la regla de juego responsable.
* Permite conservar historial sin bloquear de forma incorrecta.

Contras:

* Requiere una funcion de servicio.
* Requiere usar la misma logica en API y portal.

## Decision

Se eligio calcular la vigencia usando `activa` y `fecha_fin`, centralizando la consulta en `apps/responsible_gaming/services.py`.

## Consecuencias

Se vuelve mas facil:

* Mostrar correctamente la autoexclusion vigente en la web.
* Evitar bloqueos incorrectos por autoexclusiones vencidas.
* Reutilizar la misma logica en API y portal.

Se vuelve mas dificil:

* Hay que recordar usar el servicio en lugar de consultar solo activa=True.

Deuda tecnica:

* En una version futura se podria agregar una tarea programada para marcar como inactivas las autoexclusiones vencidas.
* Por ahora se calcula la vigencia en tiempo real sin modificar registros historicos.

## Fecha y autor

Fecha: 2026-05-28.
Autor: Eduardo Puicon Paico.
