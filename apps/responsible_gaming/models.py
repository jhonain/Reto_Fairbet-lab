import uuid
from decimal import Decimal
from datetime import timedelta
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from .choices import TipoExclusion, PeriodoLimite
Usuario = get_user_model()

class EstadoActividadSospechosa(models.TextChoices):
    PENDIENTE = ('pendiente', 'Pendiente')
    REVISADO = ('revisado', 'Revisado')
    DESCARTADO = ('descartado', 'Descartado')

class AutoExclusion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey(Usuario, on_delete=models.PROTECT, related_name='exclusiones', verbose_name='Usuario')
    tipo = models.CharField(max_length=20, choices=TipoExclusion.choices, verbose_name='Tipo de exclusion')
    fecha_inicio = models.DateTimeField(default=timezone.now, verbose_name='Fecha de inicio')
    fecha_fin = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de fin')
    activa = models.BooleanField(default=True, verbose_name='Activa')
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creacion')

    class Meta:
        db_table = 'usuarios_autoexclusion'
        verbose_name = 'Autoexclusion'
        verbose_name_plural = 'Autoexclusiones'
        indexes = [models.Index(fields=['usuario', 'activa', 'fecha_fin'])]

    def clean(self):
        super().clean()
        if self.tipo != TipoExclusion.INDEFINIDA and (not self.fecha_fin):
            raise ValidationError('Las exclusiones temporales deben tener fecha de fin.')
        if self.tipo == TipoExclusion.INDEFINIDA and self.fecha_fin:
            raise ValidationError('Las exclusiones indefinidas no deben tener fecha de fin.')

    def save(self, *args, **kwargs):
        if not self.fecha_fin and self.tipo != TipoExclusion.INDEFINIDA:
            dias_map = {'temporal_7': 7, 'temporal_30': 30, 'temporal_90': 90}
            dias = dias_map.get(self.tipo)
            if dias:
                self.fecha_fin = self.fecha_inicio + timedelta(days=dias)
        self.clean()
        super().save(*args, **kwargs)

    @property
    def esta_vigente(self):
        if not self.activa:
            return False
        if self.fecha_fin is None:
            return True
        return self.fecha_fin > timezone.now()

    def desactivar(self):
        self.activa = False
        self.save(update_fields=['activa'])

class SuspiciousActivity(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey(Usuario, on_delete=models.PROTECT, null=True, blank=True, related_name='actividades_sospechosas', verbose_name='Usuario')
    regla = models.CharField(max_length=80, verbose_name='Regla')
    descripcion = models.TextField(verbose_name='Descripcion')
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='Direccion IP')
    metadata = models.JSONField(default=dict, blank=True, verbose_name='Metadata')
    estado = models.CharField(max_length=20, choices=EstadoActividadSospechosa.choices, default=EstadoActividadSospechosa.PENDIENTE, verbose_name='Estado')
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creacion')

    class Meta:
        db_table = 'responsible_gaming_suspiciousactivity'
        verbose_name = 'Actividad sospechosa'
        verbose_name_plural = 'Actividades sospechosas'
        indexes = [models.Index(fields=['regla', 'ip_address', 'fecha_creacion']), models.Index(fields=['estado', 'fecha_creacion'])]

    def __str__(self):
        return f'{self.regla} - {self.estado}'

class LimiteDeposito(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey(Usuario, on_delete=models.PROTECT, related_name='limites_deposito', verbose_name='Usuario')
    periodo = models.CharField(max_length=10, choices=PeriodoLimite.choices, verbose_name='Periodo')
    monto = models.DecimalField(max_digits=18, decimal_places=4, verbose_name='Monto limite')
    monto_pendiente = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True, verbose_name='Monto pendiente')
    pendiente_desde = models.DateTimeField(null=True, blank=True, verbose_name='Pendiente desde')
    pendiente_aplicable_desde = models.DateTimeField(null=True, blank=True, verbose_name='Pendiente aplicable desde')
    enfriamiento_hasta = models.DateTimeField(null=True, blank=True, verbose_name='Enfriamiento hasta')
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name='Ultima actualizacion')

    class Meta:
        db_table = 'usuarios_limitedeposito'
        unique_together = [['usuario', 'periodo']]
        verbose_name = 'Limite de deposito'
        verbose_name_plural = 'Limites de deposito'

    def puede_aumentar(self) -> bool:
        if not self.enfriamiento_hasta:
            return True
        return timezone.now() >= self.enfriamiento_hasta

    def puede_aplicar_aumento_pendiente(self) -> bool:
        if not self.monto_pendiente or not self.pendiente_aplicable_desde:
            return False
        return timezone.now() >= self.pendiente_aplicable_desde

    def actualizar_monto(self, nuevo_monto: Decimal):
        if nuevo_monto <= 0:
            raise ValidationError('El monto debe ser positivo.')
        if nuevo_monto < self.monto:
            self.monto = nuevo_monto
            self.monto_pendiente = None
            self.pendiente_desde = None
            self.pendiente_aplicable_desde = None
            self.enfriamiento_hasta = None
        elif nuevo_monto > self.monto:
            ahora = timezone.now()
            aplicable_desde = ahora + timedelta(hours=24)
            self.monto_pendiente = nuevo_monto
            self.pendiente_desde = ahora
            self.pendiente_aplicable_desde = aplicable_desde
            self.enfriamiento_hasta = aplicable_desde
        else:
            return
        self.save()

    def aplicar_aumento_pendiente(self):
        if not self.monto_pendiente:
            raise ValidationError('No hay aumento pendiente para aplicar.')
        if not self.puede_aplicar_aumento_pendiente():
            raise ValidationError(f"El aumento pendiente estara disponible desde: {self.pendiente_aplicable_desde.strftime('%Y-%m-%d %H:%M')}")
        self.monto = self.monto_pendiente
        self.monto_pendiente = None
        self.pendiente_desde = None
        self.pendiente_aplicable_desde = None
        self.enfriamiento_hasta = None
        self.save()
