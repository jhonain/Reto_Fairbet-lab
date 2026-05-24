from django.db import models

class KYCStatus(models.TextChoices):
    PENDING     = "pendiente_verificacion", "Pendiente de verificación"
    VERIFIED    = "verificado",             "Verificado"
    BLOCKED     = "bloqueado",              "Bloqueado"
    EXCLUDED    = "autoexcluido",           "Autoexcluido"

class ExclusionType(models.TextChoices):
    DAYS_7      = "temporal_7",    "Temporal 7 días"
    DAYS_30     = "temporal_30",   "Temporal 30 días"
    DAYS_90     = "temporal_90",   "Temporal 90 días"
    INDEFINITE  = "indefinida",    "Indefinida"


class LimitPeriod(models.TextChoices):
    DAILY   = "daily",   "Diario"
    WEEKLY  = "weekly",  "Semanal"
    MONTHLY = "monthly", "Mensual"