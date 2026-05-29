import uuid
from decimal import Decimal
from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from .choices import TipoExclusion, PeriodoLimite
Usuario = get_user_model()

class AutoExclusion(models.Model):
    """
    Registro de autoexclusión del usuario.
    Histórico: un usuario puede tener múltiples exclusiones (activas o pasadas).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey(
        Usuario,  # ← Apunta al Usuario, no al Perfil
        on_delete=models.PROTECT,
        related_name="exclusiones",
        verbose_name="Usuario"
    )
    tipo = models.CharField(
        max_length=20,
        choices=TipoExclusion.choices,
        verbose_name="Tipo de exclusión"
    )
    fecha_inicio = models.DateTimeField(
        default=timezone.now,
        verbose_name="Fecha de inicio"
    )
    fecha_fin = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de fin"
    )
    activa = models.BooleanField(
        default=True,
        verbose_name="¿Activa?"
    )
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de creación"
    )

    class Meta:
        db_table = "usuarios_autoexclusion"
        verbose_name = "Autoexclusión"
        verbose_name_plural = "Autoexclusiones"
        indexes = [
            models.Index(fields=["usuario", "activa", "fecha_fin"]),
        ]

    def clean(self):
        """Validaciones antes de guardar."""
        super().clean()
        # Validar que temporal tenga fecha_fin, indefinida no
        if self.tipo != TipoExclusion.INDEFINIDA and not self.fecha_fin:
            raise ValidationError(
                "Las exclusiones temporales deben tener fecha de fin."
            )
        if self.tipo == TipoExclusion.INDEFINIDA and self.fecha_fin:
            raise ValidationError(
                "Las exclusiones indefinidas no deben tener fecha de fin."
            )

    def save(self, *args, **kwargs):
        # Primero calculamos fecha_fin, luego validamos
        if not self.fecha_fin and self.tipo != TipoExclusion.INDEFINIDA:
            dias_map = {
                "temporal_7": 7,
                "temporal_30": 30,
                "temporal_90": 90,
            }
            dias = dias_map.get(self.tipo)
            if dias:
                self.fecha_fin = self.fecha_inicio + timedelta(days=dias)
        self.clean()
        super().save(*args, **kwargs)

    def desactivar(self):
        """Desactiva la exclusión (solo admin, no el usuario)."""
        self.activa = False
        self.save(update_fields=["activa"])


class LimiteDeposito(models.Model):
    """
    Límites de depósito configurables por el usuario.
    Solo se puede bajar instantáneamente; subir requiere 24h de cooldown.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey(
        Usuario,  # ← Apunta al Usuario, no al Perfil
        on_delete=models.PROTECT,
        related_name="limites_deposito",
        verbose_name="Usuario"
    )
    periodo = models.CharField(
        max_length=10,
        choices=PeriodoLimite.choices,
        verbose_name="Período"
    )
    monto = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        verbose_name="Monto límite"
    )
    enfriamiento_hasta = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Enfriamiento hasta (cooldown)"
    )
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name="Última actualización"
    )

    class Meta:
        db_table = "usuarios_limitedeposito"
        unique_together = [["usuario", "periodo"]]
        verbose_name = "Límite de depósito"
        verbose_name_plural = "Límites de depósito"

    def puede_aumentar(self) -> bool:
        """Verifica si ya pasó el período de enfriamiento."""
        if not self.enfriamiento_hasta:
            return True
        return timezone.now() >= self.enfriamiento_hasta

    def actualizar_monto(self, nuevo_monto: Decimal):
        """
        Actualiza el límite de depósito.
        - Bajar: instantáneo
        - Subir: requiere 24h de enfriamiento
        """
        if nuevo_monto < self.monto:
            # Bajar límite: instantáneo
            self.monto = nuevo_monto
            self.enfriamiento_hasta = None
        elif nuevo_monto > self.monto:
            # Subir límite: requiere cooldown
            if not self.puede_aumentar():
                dias_restantes = (self.enfriamiento_hasta - timezone.now()).days
                raise ValidationError(
                    f"Debes esperar {dias_restantes} días para aumentar el límite. "
                    f"Enfriamiento hasta: {self.enfriamiento_hasta.strftime('%Y-%m-%d %H:%M')}"
                )
            self.monto = nuevo_monto
            self.enfriamiento_hasta = timezone.now() + timedelta(hours=24)
        # Si es igual, no hacer nada
        self.save()