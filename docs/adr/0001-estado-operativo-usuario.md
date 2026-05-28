# ADR 0001: Estado operativo del usuario

## Contexto

El sistema ya bloquea apuestas desde backend cuando una cuenta no está habilitada para apostar. Esa validación existe en el flujo de apuestas y usa el estado del perfil del usuario.

El problema era que el usuario no veía claramente en la interfaz si podía apostar o por qué estaba bloqueado. Esto podía generar confusión en casos como cuenta pendiente de verificación, cuenta bloqueada o autoexclusión activa.

En esta fase solo se muestra el estado operativo en el portal y se bloquea visualmente la apuesta en la pantalla de eventos. No se modifica wallet, betting, responsible_gaming ni los modelos.

## Opciones consideradas

### Opción 1: Poner la lógica directamente en las vistas y templates


* Es rápido de implementar.
* Requiere menos archivos.
pero a consecuencia de ello
* Duplica lógica.
* Es más difícil de mantener.
* El template tendría demasiada responsabilidad.

### Opción 2: Crear un servicio simple en apps/users/services.py
se podria
* Centralizar la lógica.
* Reutilizar en perfil, eventos, wallet o betting.
* Es más fácil de explicar y mantener.

pero 
* Agrega un archivo nuevo.
* Requiere importar el servicio donde se use.

## Decisión

Se eligió crear un servicio simple en `apps/users/services.py` para calcular el estado operativo del usuario.

Se vuelve más fácil:

* Mostrar en el portal si el usuario puede apostar o no.
* Reutilizar la misma lógica en perfil y eventos.
* Explicar al usuario el motivo del bloqueo.

lo dificil sera: 

* Hay que importar el servicio en las vistas donde se quiera mostrar el estado operativo.

## Deuda técnica

* Todavía falta integrar esta misma validación visual o de servicio en otras operaciones sensibles si el equipo lo requiere, como recargas, retiros o transferencias.
* Todavía falta decidir si autoexcluido será un estado guardado en `PerfilUsuario` o seguirá siendo un estado calculado desde `AutoExclusion`.
* En esta fase no se agregó el estado `autoexcluido` a `EstadoKYC`; la autoexclusión se detecta desde `AutoExclusion`.
* Esta fase no reemplaza la validación backend del servicio de apuestas; solo mejora la información visible y el bloqueo visual en el portal.
