from django.db import models

class TipoCuenta(models.TextChoices):
    BILLETERA_USUARIO = ('billetera_usuario', 'Billetera de usuario')
    CASA = ('casa', 'Cuenta de la casa')
    APUESTAS_PENDIENTES = ('apuestas_pendientes', 'Apuestas pendientes')
    BONOS = ('bonos', 'Bonos')

class DireccionAsiento(models.TextChoices):
    DEBITO = ('DEBITO', 'Débito (salida)')
    CREDITO = ('CREDITO', 'Crédito (entrada)')

class TipoAsiento(models.TextChoices):
    RECARGA = ('recarga', 'Recarga de fichas')
    RETIRO = ('retiro', 'Retiro simulado de fichas')
    TRANSFERENCIA = ('transferencia', 'Transferencia entre usuarios')
    BLOQUEO_APUESTA = ('bloqueo_apuesta', 'Bloqueo por apuesta')
    GANANCIA_APUESTA = ('ganancia_apuesta', 'Ganancia de apuesta')
    PERDIDA_APUESTA = ('perdida_apuesta', 'Pérdida de apuesta')
    CASH_OUT = ('cash_out', 'Cash-out anticipado')
    BONO_ACREDITADO = ('bono_acreditado', 'Abono de bono')
    BONO_DEBITADO = ('bono_debitado', 'Débito de bono')
