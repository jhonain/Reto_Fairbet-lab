import uuid
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from apps.events.models import Cuota, Evento
from apps.events.choices import EstadoEvento, EstadoMercado
from apps.wallet.models import ServicioBilletera, asegurar_cuenta_usuario
from apps.responsible_gaming.constants import MENSAJE_CONSUMO_RESPONSABLE
from .models import Apuesta, PiernaApuesta
from .choices import EstadoApuesta, TipoApuesta

MONTO_MINIMO = Decimal('1.0000')
MONTO_MAXIMO = Decimal('5000.0000')
FACTOR_CASA_CASH_OUT = Decimal('0.80')

def _auditar(evento, payload):
    from apps.dashboard.services import registrar_auditoria
    registrar_auditoria(evento, payload)

@transaction.atomic
def crear_apuesta_simple(usuario, cuota_id, monto: Decimal, clave_idempotencia: str, acepto_juego_responsable: bool):
    if Apuesta.objects.filter(clave_idempotencia=clave_idempotencia).exists():
        return Apuesta.objects.get(clave_idempotencia=clave_idempotencia)
    if not acepto_juego_responsable:
        raise ValidationError('Debes confirmar el mensaje de consumo responsable.')
    perfil = getattr(usuario, 'perfil', None)
    if perfil is None or not perfil.puede_apostar:
        raise ValidationError('Cuenta no habilitada para apostar (KYC o autoexclusión).')
    if monto < MONTO_MINIMO or monto > MONTO_MAXIMO:
        raise ValidationError(f'Monto fuera de rango ({MONTO_MINIMO} - {MONTO_MAXIMO}).')
    cuota = Cuota.objects.select_related('mercado__evento').get(pk=cuota_id)
    evento = cuota.mercado.evento
    if evento.estado != EstadoEvento.PROGRAMADO:
        raise ValidationError('Solo se aceptan apuestas en eventos programados (pre-partido).')
    if not evento.estan_apuestas_abiertas:
        raise ValidationError('Las apuestas están cerradas para este evento.')
    if cuota.mercado.estado != EstadoMercado.ABIERTO or not cuota.activa:
        raise ValidationError('Mercado o cuota no disponible.')
    asegurar_cuenta_usuario(usuario)
    id_apuesta = uuid.uuid4()
    clave_wallet = uuid.uuid4()
    ServicioBilletera.bloquear_para_apuesta(usuario, monto, id_apuesta, clave_wallet)
    apuesta = Apuesta.objects.create(usuario=usuario, tipo=TipoApuesta.SIMPLE, estado=EstadoApuesta.ACEPTADA, monto_apostado=monto, cuota_total=cuota.valor, clave_idempotencia=clave_idempotencia, verificacion_juego_responsable=True, fecha_aceptacion=timezone.now())
    apuesta.calcular_ganancia_potencial()
    apuesta.save(update_fields=['ganancia_potencial'])
    PiernaApuesta.objects.create(apuesta=apuesta, cuota=cuota, cuota_al_momento=cuota.valor)
    _auditar('apuesta_simple_creada', f'apuesta={apuesta.id} usuario={usuario.username} stake={monto} cuota={cuota.valor}')
    apuesta._mensaje_juego = MENSAJE_CONSUMO_RESPONSABLE
    return apuesta

@transaction.atomic
def crear_apuesta_combinada(usuario, cuota_ids, monto: Decimal, clave_idempotencia: str, acepto_juego_responsable: bool):
    if Apuesta.objects.filter(clave_idempotencia=clave_idempotencia).exists():
        return Apuesta.objects.get(clave_idempotencia=clave_idempotencia)
    if not acepto_juego_responsable:
        raise ValidationError('Debes confirmar el mensaje de consumo responsable.')
    ids_unicos = list(dict.fromkeys(cuota_ids or []))
    if len(ids_unicos) < 2:
        raise ValidationError('Una combinada requiere al menos 2 selecciones.')
    perfil = getattr(usuario, 'perfil', None)
    if perfil is None or not perfil.puede_apostar:
        raise ValidationError('Cuenta no habilitada para apostar (KYC o autoexclusión).')
    if monto < MONTO_MINIMO or monto > MONTO_MAXIMO:
        raise ValidationError(f'Monto fuera de rango ({MONTO_MINIMO} - {MONTO_MAXIMO}).')
    cuotas = list(Cuota.objects.select_related('mercado__evento').filter(pk__in=ids_unicos))
    if len(cuotas) != len(ids_unicos):
        raise ValidationError('Una o más cuotas no existen.')
    eventos_vistos = set()
    cuota_total = Decimal('1.0000')
    for cuota in cuotas:
        evento = cuota.mercado.evento
        if evento.id in eventos_vistos:
            raise ValidationError('No se permite más de una selección del mismo evento en una combinada.')
        eventos_vistos.add(evento.id)
        if evento.estado != EstadoEvento.PROGRAMADO:
            raise ValidationError('Solo se aceptan apuestas en eventos programados (pre-partido).')
        if not evento.estan_apuestas_abiertas:
            raise ValidationError('Las apuestas están cerradas para una de las selecciones.')
        if cuota.mercado.estado != EstadoMercado.ABIERTO or not cuota.activa:
            raise ValidationError('Mercado o cuota no disponible en una selección.')
        cuota_total *= cuota.valor
    cuota_total = cuota_total.quantize(Decimal('0.0001'))
    asegurar_cuenta_usuario(usuario)
    id_apuesta = uuid.uuid4()
    clave_wallet = uuid.uuid4()
    ServicioBilletera.bloquear_para_apuesta(usuario, monto, id_apuesta, clave_wallet)
    apuesta = Apuesta.objects.create(usuario=usuario, tipo=TipoApuesta.COMBINADA, estado=EstadoApuesta.ACEPTADA, monto_apostado=monto, cuota_total=cuota_total, clave_idempotencia=clave_idempotencia, verificacion_juego_responsable=True, fecha_aceptacion=timezone.now())
    apuesta.calcular_ganancia_potencial()
    apuesta.save(update_fields=['ganancia_potencial'])
    for cuota in cuotas:
        PiernaApuesta.objects.create(apuesta=apuesta, cuota=cuota, cuota_al_momento=cuota.valor)
    _auditar('apuesta_combinada_creada', f'apuesta={apuesta.id} usuario={usuario.username} stake={monto} cuota_total={cuota_total}')
    apuesta._mensaje_juego = MENSAJE_CONSUMO_RESPONSABLE
    return apuesta

@transaction.atomic
def liquidar_apuesta(apuesta_id, gano: bool):
    apuesta = Apuesta.objects.select_for_update().get(pk=apuesta_id)
    if apuesta.estado not in (EstadoApuesta.ACEPTADA,):
        raise ValidationError('La apuesta ya fue liquidada.')
    clave = uuid.uuid4()
    stake = apuesta.monto_apostado
    if gano:
        payout = stake * apuesta.cuota_total
        ServicioBilletera.liquidar_ganadora(apuesta.usuario, stake, payout, apuesta.id, clave)
        apuesta.estado = EstadoApuesta.GANADA
        apuesta.ganancia_real = payout
    else:
        ServicioBilletera.liquidar_perdedora(stake, apuesta.id, clave)
        apuesta.estado = EstadoApuesta.PERDIDA
        apuesta.ganancia_real = Decimal('0')
    apuesta.fecha_liquidacion = timezone.now()
    apuesta.save()
    for pierna in apuesta.piernas.all():
        pierna.es_ganadora = gano
        pierna.save(update_fields=['es_ganadora'])
        pierna.cuota.liquidar(es_ganadora=gano)
    _auditar('apuesta_liquidada', f'apuesta={apuesta.id} gano={gano} payout={apuesta.ganancia_real}')
    return apuesta

def calcular_cash_out(apuesta):
    valor = apuesta.monto_apostado * apuesta.cuota_total * FACTOR_CASA_CASH_OUT
    return valor.quantize(Decimal('0.0001'))

@transaction.atomic
def hacer_cash_out(apuesta_id):
    apuesta = Apuesta.objects.select_for_update().get(pk=apuesta_id)
    if apuesta.estado != EstadoApuesta.ACEPTADA:
        raise ValidationError('Solo se puede hacer cash-out de una apuesta aceptada.')
    monto = calcular_cash_out(apuesta)
    clave = uuid.uuid4()
    ServicioBilletera.cash_out(apuesta.usuario, apuesta.monto_apostado, monto, apuesta.id, clave)
    apuesta.estado = EstadoApuesta.CASH_OUT
    apuesta.monto_cash_out = monto
    apuesta.ganancia_real = monto
    apuesta.fecha_liquidacion = timezone.now()
    apuesta.save()
    _auditar('apuesta_cash_out', f'apuesta={apuesta.id} usuario={apuesta.usuario.username} monto_cash_out={monto}')
    return apuesta
