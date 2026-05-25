from decimal import Decimal
from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db.models import Sum
from django.utils import timezone

from apps.wallet.models import AsientoContable, Cuenta
from apps.wallet.choices import TipoAsiento, DireccionAsiento, TipoCuenta
from .choices import PeriodoLimite
from .models import LimiteDeposito


def _inicio_periodo(periodo):
    ahora = timezone.now()
    if periodo == PeriodoLimite.DIARIO:
        return ahora.replace(hour=0, minute=0, second=0, microsecond=0)
    if periodo == PeriodoLimite.SEMANAL:
        return ahora - timedelta(days=ahora.weekday())
    # mensual
    return ahora.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


def monto_recargado_en_periodo(usuario, periodo) -> Decimal:
    cuenta = Cuenta.objects.filter(
        usuario=usuario, tipo_cuenta=TipoCuenta.BILLETERA_USUARIO
    ).first()
    if not cuenta:
        return Decimal("0")

    inicio = _inicio_periodo(periodo)
    total = AsientoContable.objects.filter(
        cuenta=cuenta,
        tipo_asiento=TipoAsiento.RECARGA,
        direccion=DireccionAsiento.CREDITO,
        fecha_creacion__gte=inicio,
    ).aggregate(s=Sum("monto"))["s"]
    return total or Decimal("0")


def validar_limite_recarga(usuario, monto: Decimal):
    """Bloquea recargas que superen el límite configurado por el usuario."""
    for limite in LimiteDeposito.objects.filter(usuario=usuario):
        usado = monto_recargado_en_periodo(usuario, limite.periodo)
        if usado + monto > limite.monto:
            raise ValidationError(
                f"Límite {limite.get_periodo_display()} excedido. "
                f"Usado: {usado}, límite: {limite.monto}"
            )
