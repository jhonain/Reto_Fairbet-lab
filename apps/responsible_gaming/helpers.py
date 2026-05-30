from decimal import Decimal
from .models import LimiteDeposito
from .choices import PeriodoLimite
LIMITES_DEFECTO = {PeriodoLimite.DIARIO: Decimal('500.0000'), PeriodoLimite.SEMANAL: Decimal('2000.0000'), PeriodoLimite.MENSUAL: Decimal('8000.0000')}

def crear_limites_por_defecto(usuario):
    for periodo, monto in LIMITES_DEFECTO.items():
        LimiteDeposito.objects.get_or_create(usuario=usuario, periodo=periodo, defaults={'monto': monto})
