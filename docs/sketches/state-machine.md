# Máquinas de Estado — FairBet Lab

## 1. Evento

```mermaid
stateDiagram-v2
    [*] --> PROGRAMADO : creación
    PROGRAMADO --> EN_VIVO : inicio del evento
    PROGRAMADO --> SUSPENDIDO : operador/sistema
    PROGRAMADO --> ANULADO : cancelación
    EN_VIVO --> SUSPENDIDO : momento crítico / operador
    EN_VIVO --> FINALIZADO : término del evento
    SUSPENDIDO --> EN_VIVO : reanudación
    SUSPENDIDO --> ANULADO : cancelación definitiva
    FINALIZADO --> [*]
    ANULADO --> [*]
```

- **PROGRAMADO**: estado inicial. Apuestas abiertas (pre-partido e in-play).
- **EN_VIVO**: el evento está en curso. Apuestas abiertas (cuotas dinámicas).
- **SUSPENDIDO**: apuestas cerradas temporalmente (gol, tarjeta roja, etc.).
- **FINALIZADO**: apuestas liquidadas, no se aceptan más apuestas.
- **ANULADO**: evento cancelado, apuestas reembolsadas.

## 2. Mercado

```mermaid
stateDiagram-v2
    [*] --> ABIERTO : creación
    ABIERTO --> SUSPENDIDO : evento crítico / operador
    SUSPENDIDO --> ABIERTO : reapertura
    ABIERTO --> CERRADO : cierre de apuestas
    SUSPENDIDO --> CERRADO : cierre durante suspensión
    CERRADO --> LIQUIDADO : liquidación de cuotas
    LIQUIDADO --> [*]
```

- **ABIERTO**: se pueden realizar apuestas.
- **SUSPENDIDO**: apuestas pausadas temporalmente.
- **CERRADO**: no se aceptan más apuestas (el evento comenzó o el operador cerró).
- **LIQUIDADO**: todas las cuotas del mercado tienen resultado asignado.

## 3. Apuesta

```mermaid
stateDiagram-v2
    [*] --> PENDIENTE : creación inicial
    PENDIENTE --> ACEPTADA : confirmación + bloqueo fondos
    PENDIENTE --> CANCELADA : rechazo / error
    ACEPTADA --> GANADA : liquidación (todas las piernas ganan)
    ACEPTADA --> PERDIDA : liquidación (alguna pierna pierde)
    ACEPTADA --> CASH_OUT : usuario solicita cash-out
    CASH_OUT --> [*]
    GANADA --> [*]
    PERDIDA --> [*]
    CANCELADA --> [*]
```

- **PENDIENTE**: estado transitorio durante la creación.
- **ACEPTADA**: fondos bloqueados, apuesta activa. Puede ser simple o combinada.
- **GANADA**: el usuario ganó. Payout = `stake × cuota_total`.
- **PERDIDA**: el usuario perdió. Pérdida = `stake` (va a la casa).
- **CASH_OUT**: liquidación anticipada. El usuario recibe un monto calculado.
- **CANCELADA**: apuesta anulada por error del sistema o evento anulado.

## 4. Cuenta de usuario (estado operativo)

```mermaid
stateDiagram-v2
    [*] --> PENDIENTE_KYC : registro
    PENDIENTE_KYC --> VERIFICADO : KYC aprobado
    PENDIENTE_KYC --> BLOQUEADO : KYC rechazado
    VERIFICADO --> AUTOEXCLUIDO : autoexclusión activa
    AUTOEXCLUIDO --> VERIFICADO : fin de autoexclusión
    BLOQUEADO --> [*]
```

- **PENDIENTE_KYC**: puede ver eventos pero no apostar.
- **VERIFICADO**: puede apostar, recargar, retirar.
- **AUTOEXCLUIDO**: no puede apostar ni recargar (solo retirar fondos).
- **BLOQUEADO**: cuenta cerrada por KYC rechazado o decisión del operador.

## 5. Alerta de actividad sospechosa

```mermaid
stateDiagram-v2
    [*] --> PENDIENTE : detección automática
    PENDIENTE --> REVISADO : operador revisa
    REVISADO --> DESCARTADO : falso positivo
    REVISADO --> [*] : medidas tomadas
    DESCARTADO --> [*]
```

- **PENDIENTE**: alerta generada, espera revisión del operador.
- **REVISADO**: el operador ya revisó la alerta.
- **DESCARTADO**: se determinó que no era fraude.
