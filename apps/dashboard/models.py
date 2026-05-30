import uuid
from django.db import models

class RegistroAuditoria(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    evento = models.CharField(max_length=50, help_text='Tipo de evento, ej. apuesta_creada')
    payload = models.TextField(help_text='Datos del evento en texto')
    hash_anterior = models.CharField(max_length=64, blank=True)
    hash_actual = models.CharField(max_length=64, unique=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'dashboard_auditoria'
        ordering = ['fecha_creacion']
        verbose_name = 'Registro de auditoría'
        verbose_name_plural = 'Registros de auditoría'

    def __str__(self):
        return f'{self.evento} [{self.hash_actual[:8]}...]'
