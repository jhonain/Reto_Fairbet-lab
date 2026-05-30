from django.db import models

class EstadoApuesta(models.TextChoices):
    PENDIENTE = ('pendiente', 'Pendiente de confirmación')
    ACEPTADA = ('aceptada', 'Aceptada')
    GANADA = ('ganada', 'Ganada')
    PERDIDA = ('perdida', 'Perdida')
    CASH_OUT = ('cash_out', 'Cash-out')
    CANCELADA = ('cancelada', 'Cancelada')

class TipoApuesta(models.TextChoices):
    SIMPLE = ('simple', 'Simple')
    COMBINADA = ('combinada', 'Combinada')
