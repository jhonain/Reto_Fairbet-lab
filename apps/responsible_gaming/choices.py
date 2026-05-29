from django.db import models

class TipoExclusion(models.TextChoices):
    TEMPORAL_7 = "temporal_7", "Temporal (7 días)"
    TEMPORAL_30 = "temporal_30", "Temporal (30 días)"
    TEMPORAL_90 = "temporal_90", "Temporal (90 días)"
    INDEFINIDA = "indefinida", "Indefinida"


class PeriodoLimite(models.TextChoices):
    DIARIO = "diario", "Diario"
    SEMANAL = "semanal", "Semanal"
    MENSUAL = "mensual", "Mensual"