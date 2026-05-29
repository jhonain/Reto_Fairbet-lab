import uuid
from decimal import Decimal
from django.db import models
from django.contrib.auth import get_user_model
from .choices import TipoApuesta, EstadoApuesta
from apps.events.models import Cuota

Usuario = get_user_model()


class Apuesta(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        related_name="apuestas",
        verbose_name="Usuario"
    )
    tipo = models.CharField(
        max_length=20,
        choices=TipoApuesta.choices,
        default=TipoApuesta.SIMPLE,
        verbose_name="Tipo de apuesta"
    )
    estado = models.CharField(
        max_length=20,
        choices=EstadoApuesta.choices,
        default=EstadoApuesta.PENDIENTE,
        verbose_name="Estado"
    )
    
    # Montos
    monto_apostado = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        verbose_name="Monto apostado (stake)"
    )
    cuota_total = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        default=Decimal("1.0000"),
        verbose_name="Cuota total"
    )
    ganancia_potencial = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        default=Decimal("0.0000"),
        verbose_name="Ganancia potencial"
    )
    ganancia_real = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        null=True,
        blank=True,
        verbose_name="Ganancia real (payout)"
    )
    monto_cash_out = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        null=True,
        blank=True,
        verbose_name="Monto de cash-out"
    )
    
    # Control de tiempo
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    fecha_aceptacion = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de aceptación")
    fecha_liquidacion = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de liquidación")
    
    # Idempotencia
    clave_idempotencia = models.CharField(
        max_length=64,
        unique=True,
        db_index=True,
        verbose_name="Clave de idempotencia"
    )
    
    # Juego responsable
    verificacion_juego_responsable = models.BooleanField(
        default=False,
        verbose_name="¿Verificó juego responsable?"
    )

    class Meta:
        db_table = "apuestas_apuesta"
        verbose_name = "Apuesta"
        verbose_name_plural = "Apuestas"
        indexes = [
            models.Index(fields=["usuario", "estado", "fecha_creacion"]),
            models.Index(fields=["estado", "fecha_liquidacion"]),
        ]

    def calcular_ganancia_potencial(self):
        self.ganancia_potencial = self.monto_apostado * self.cuota_total
        return self.ganancia_potencial


class PiernaApuesta(models.Model):
    """Cada selección dentro de una apuesta (simple o combinada)."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    apuesta = models.ForeignKey(
        Apuesta,
        on_delete=models.CASCADE,
        related_name="piernas",
        verbose_name="Apuesta"
    )
    cuota = models.ForeignKey(
        Cuota,
        on_delete=models.PROTECT,
        verbose_name="Cuota seleccionada"
    )
    cuota_al_momento = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        verbose_name="Cuota al momento de la apuesta"
    )
    es_ganadora = models.BooleanField(
        null=True,
        blank=True,
        default=None,
        verbose_name="¿Es ganadora?"
    )

    class Meta:
        db_table = "apuestas_pierna"
        verbose_name = "Pierna de apuesta"
        verbose_name_plural = "Piernas de apuestas"
        unique_together = [["apuesta", "cuota"]]