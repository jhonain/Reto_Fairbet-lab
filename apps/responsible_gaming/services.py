from decimal import Decimal
from datetime import timedelta
from django.core.exceptions import ValidationError
from django.db.models import Q, Sum
from django.utils import timezone
from apps.wallet.models import AsientoContable, Cuenta
from apps.wallet.choices import TipoAsiento, DireccionAsiento, TipoCuenta
from .choices import PeriodoLimite
from .models import AutoExclusion, SuspiciousActivity, LimiteDeposito
UMBRAL_MULTIPLES_CUENTAS_IP = 3
REGLA_REGISTRO_IP = 'registro_ip'
REGLA_MULTIPLES_CUENTAS_IP = 'multiples_cuentas_ip'

def _inicio_periodo(periodo):
    ahora = timezone.now()
    if periodo == PeriodoLimite.DIARIO:
        return ahora.replace(hour=0, minute=0, second=0, microsecond=0)
    if periodo == PeriodoLimite.SEMANAL:
        return ahora - timedelta(days=ahora.weekday())
    return ahora.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

def monto_recargado_en_periodo(usuario, periodo) -> Decimal:
    cuenta = Cuenta.objects.filter(usuario=usuario, tipo_cuenta=TipoCuenta.BILLETERA_USUARIO).first()
    if not cuenta:
        return Decimal('0')
    inicio = _inicio_periodo(periodo)
    total = AsientoContable.objects.filter(cuenta=cuenta, tipo_asiento=TipoAsiento.RECARGA, direccion=DireccionAsiento.CREDITO, fecha_creacion__gte=inicio).aggregate(s=Sum('monto'))['s']
    return total or Decimal('0')

def validar_limite_recarga(usuario, monto: Decimal):
    if obtener_autoexclusion_vigente(usuario):
        raise ValidationError('No puedes recargar porque tienes una autoexclusion vigente.')
    for limite in LimiteDeposito.objects.filter(usuario=usuario):
        usado = monto_recargado_en_periodo(usuario, limite.periodo)
        if usado + monto > limite.monto:
            raise ValidationError(f'Límite {limite.get_periodo_display()} excedido. Usado: {usado}, límite: {limite.monto}')

def obtener_autoexclusion_vigente(usuario):
    return AutoExclusion.objects.filter(usuario=usuario, activa=True).filter(Q(fecha_fin__isnull=True) | Q(fecha_fin__gt=timezone.now())).order_by('-fecha_creacion').first()

def registrar_alerta_multiples_cuentas_ip(usuario, ip_address):
    if not ip_address:
        return None
    registro, _ = SuspiciousActivity.objects.get_or_create(usuario=usuario, regla=REGLA_REGISTRO_IP, ip_address=ip_address, defaults={'descripcion': 'Registro de usuario asociado a una direccion IP.', 'metadata': {'usuario_id': usuario.id}, 'estado': 'revisado'})
    usuarios_en_ip = SuspiciousActivity.objects.filter(regla=REGLA_REGISTRO_IP, ip_address=ip_address).values('usuario').distinct().count()
    if usuarios_en_ip < UMBRAL_MULTIPLES_CUENTAS_IP:
        return registro
    alerta_existente = SuspiciousActivity.objects.filter(usuario=usuario, regla=REGLA_MULTIPLES_CUENTAS_IP, ip_address=ip_address).exists()
    if alerta_existente:
        return registro
    return SuspiciousActivity.objects.create(usuario=usuario, regla=REGLA_MULTIPLES_CUENTAS_IP, descripcion='Se detectaron varias cuentas registradas desde la misma direccion IP.', ip_address=ip_address, metadata={'usuarios_en_ip': usuarios_en_ip, 'umbral': UMBRAL_MULTIPLES_CUENTAS_IP})
