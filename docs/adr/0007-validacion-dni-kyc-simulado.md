# ADR 0007: Validacion de DNI en KYC simulado

## Contexto

El sistema rechazaba DNI reales porque interpretaba el ultimo digito de los 8 digitos como digito verificador obligatorio. Para la demo academica, el formulario recibe un DNI de 8 digitos y debe validar formato numerico sin bloquear usuarios reales por una interpretacion incorrecta del digito verificador.

## Opciones consideradas

Opcion 1: Mantener comparacion del ultimo digito como digito verificador.

Pros:

* Parece una validacion mas estricta.
* Ya estaba implementada.

Contras:

* Rechaza DNI reales en la demo.
* Confunde el numero de DNI con un digito verificador separado.
* Bloquea el registro de usuarios validos.

Opcion 2: Validar DNI como 8 digitos numericos en el KYC simulado.

Pros:

* Permite registrar DNI reales de 8 digitos.
* Rechaza letras y formatos invalidos.
* Es simple y defendible para una plataforma educativa.
* Evita falsos negativos durante la exposicion.

Contras:

* No valida contra una fuente oficial externa.
* El digito verificador queda como mejora futura si se agrega un campo separado.

## Decision

Se eligio validar el DNI como 8 digitos numericos para el KYC simulado, evitando rechazar DNI reales por una interpretacion incorrecta del digito verificador.

## Consecuencias

Se vuelve mas facil:

* Registrar usuarios reales durante la demo.
* Mantener una validacion clara y entendible.
* Evitar falsos rechazos.

Se vuelve mas dificil:

* Si el docente exige digito verificador separado, se debera agregar un campo adicional o una integracion mas completa.

Deuda tecnica:

* En una version futura se podria agregar un campo separado para digito verificador o consultar una fuente oficial si el alcance del proyecto lo permite.

## Fecha y autor

Fecha: 2026-05-28.
Autor: Eduardo Puicon Paico.
