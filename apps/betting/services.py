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

# Límites de stake (fichas virtuales) — decisión de equipo, documentar en ADR
MONTO_MINIMO = Decimal("1.0000")
MONTO_MAXIMO = Decimal("5000.0000")


@transaction.atomic
def crear_apuesta_simple(
    usuario,
    cuota_id,
    monto: Decimal,
    clave_idempotencia: str,
    acepto_juego_responsable: bool,
):
    if Apuesta.objects.filter(clave_idempotencia=clave_idempotencia).exists():
        return Apuesta.objects.get(clave_idempotencia=clave_idempotencia)

    if not acepto_juego_responsable:
        raise ValidationError("Debes confirmar el mensaje de consumo responsable.")

    perfil = getattr(usuario, "perfil", None)
    if perfil is None or not perfil.puede_apostar:
        raise ValidationError("Cuenta no habilitada para apostar (KYC o autoexclusión).")

    if monto < MONTO_MINIMO or monto > MONTO_MAXIMO:
        raise ValidationError(f"Monto fuera de rango ({MONTO_MINIMO} - {MONTO_MAXIMO}).")

    cuota = Cuota.objects.select_related("mercado__evento").get(pk=cuota_id)
    evento = cuota.mercado.evento

    if evento.estado != EstadoEvento.PROGRAMADO:
        raise ValidationError("Solo se aceptan apuestas en eventos programados (pre-partido).")

    if not evento.estan_apuestas_abiertas:
        raise ValidationError("Las apuestas están cerradas para este evento.")

    if cuota.mercado.estado != EstadoMercado.ABIERTO or not cuota.activa:
        raise ValidationError("Mercado o cuota no disponible.")

    asegurar_cuenta_usuario(usuario)
    id_apuesta = uuid.uuid4()
    clave_wallet = uuid.uuid4()

    ServicioBilletera.bloquear_para_apuesta(
        usuario, monto, id_apuesta, clave_wallet
    )

    apuesta = Apuesta.objects.create(
        usuario=usuario,
        tipo=TipoApuesta.SIMPLE,
        estado=EstadoApuesta.ACEPTADA,
        monto_apostado=monto,
        cuota_total=cuota.valor,
        clave_idempotencia=clave_idempotencia,
        verificacion_juego_responsable=True,
        fecha_aceptacion=timezone.now(),
    )
    apuesta.calcular_ganancia_potencial()
    apuesta.save(update_fields=["ganancia_potencial"])

    PiernaApuesta.objects.create(
        apuesta=apuesta,
        cuota=cuota,
        cuota_al_momento=cuota.valor,
    )

    apuesta._mensaje_juego = MENSAJE_CONSUMO_RESPONSABLE
    return apuesta


@transaction.atomic
def liquidar_apuesta(apuesta_id, gano: bool):
    apuesta = Apuesta.objects.select_for_update().get(pk=apuesta_id)
    if apuesta.estado not in (EstadoApuesta.ACEPTADA,):
        raise ValidationError("La apuesta ya fue liquidada.")

    clave = uuid.uuid4()
    stake = apuesta.monto_apostado

    if gano:
        payout = stake * apuesta.cuota_total
        ServicioBilletera.liquidar_ganadora(
            apuesta.usuario, stake, payout, apuesta.id, clave
        )
        apuesta.estado = EstadoApuesta.GANADA
        apuesta.ganancia_real = payout
    else:
        ServicioBilletera.liquidar_perdedora(stake, apuesta.id, clave)
        apuesta.estado = EstadoApuesta.PERDIDA
        apuesta.ganancia_real = Decimal("0")

    apuesta.fecha_liquidacion = timezone.now()
    apuesta.save()

    pierna = apuesta.piernas.first()
    if pierna:
        pierna.es_ganadora = gano
        pierna.save(update_fields=["es_ganadora"])
        pierna.cuota.liquidar(es_ganadora=gano)

    return apuesta
