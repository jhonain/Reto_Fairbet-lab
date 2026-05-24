import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from .validators import validate_dni, validate_age
from .choices import KYCStatus, ExclusionType, LimitPeriod


User = get_user_model()

class UserProfile(models.Model):
    id              = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user            = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    dni             = models.CharField(max_length=8, unique=True, validators=[validate_dni])
    birth_date      = models.DateField(validators=[validate_age])
    kyc_status      = models.CharField(max_length=30, choices=KYCStatus.choices, default=KYCStatus.PENDING)
    kyc_verified_at = models.DateTimeField(null=True, blank=True)
    phone           = models.CharField(max_length=20, blank=True)
    created_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "accounts_userprofile"

    def __str__(self):
        return f"{self.user.username} [{self.kyc_status}]"

    @property
    def is_betting_allowed(self) -> bool:
        """Verificar si el usuario puede apostar en este momento."""
        if self.kyc_status != KYCStatus.VERIFIED:
            return False
        active_exclusion = self.selfexclusion_set.filter(
            is_active=True
        ).filter(
            models.Q(ends_at__isnull=True) | models.Q(ends_at__gt=timezone.now())
        ).exists()
        return not active_exclusion

class SelfExclusion(models.Model):
    id             = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user           = models.ForeignKey(UserProfile, on_delete=models.PROTECT)
    exclusion_type = models.CharField(max_length=20, choices=ExclusionType.choices)
    starts_at      = models.DateTimeField(default=timezone.now)
    ends_at        = models.DateTimeField(null=True, blank=True)  # null = indefinida
    is_active      = models.BooleanField(default=True)

    class Meta:
        db_table = "accounts_selfexclusion"

    def save(self, *args, **kwargs):
        # Calcular ends_at automáticamente según tipo
        if not self.ends_at and self.exclusion_type != ExclusionType.INDEFINITE:
            days_map = {"temporal_7": 7, "temporal_30": 30, "temporal_90": 90}
            days = days_map.get(self.exclusion_type)
            if days:
                self.ends_at = self.starts_at + timedelta(days=days)
        super().save(*args, **kwargs)
        # Actualizar estado del perfil
        self.user.kyc_status = KYCStatus.EXCLUDED
        self.user.save(update_fields=["kyc_status"])


class DepositLimit(models.Model):
    id             = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user           = models.ForeignKey(UserProfile, on_delete=models.PROTECT)
    period         = models.CharField(max_length=10, choices=LimitPeriod.choices)
    amount         = models.DecimalField(max_digits=18, decimal_places=4)
    cooldown_until = models.DateTimeField(null=True, blank=True)
    updated_at     = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "accounts_depositlimit"
        unique_together = [["user", "period"]]

    def can_increase(self) -> bool:
        """Solo se puede subir el límite después del cooldown de 24h."""
        if not self.cooldown_until:
            return True
        return timezone.now() >= self.cooldown_until

    def update_limit(self, new_amount):
        """Baja instantánea. Sube requiere cooldown."""
        if new_amount < self.amount:
            self.amount = new_amount
            self.cooldown_until = None
        else:
            if not self.can_increase():
                raise ValidationError("Debes esperar el período de enfriamiento (24h) para aumentar el límite.")
            self.amount = new_amount
            self.cooldown_until = timezone.now() + timedelta(hours=24)
        self.save()