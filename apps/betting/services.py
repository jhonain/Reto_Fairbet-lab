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

MONTO_MINIMO = Decimal("1.00")
MONTO_MAXIMO = Decimal("5000.00")
MARGEN_CASH_OUT = Decimal("0.03")


def _aplicar_recotizacion(cuota, cuota_aceptada: Decimal) -> Decimal:
    cuota_actual = cuota.valor
    if cuota_actual >= cuota_aceptada:
        return cuota_actual
    return cuota_aceptada


@transaction.atomic
def crear_apuesta_simple(
    usuario,
    cuota_id,
    monto: Decimal,
    clave_idempotencia: str,
    acepto_juego_responsable: bool,
    cuota_aceptada: Decimal = None,
):
    existente = Apuesta.objects.filter(clave_idempotencia=clave_idempotencia).first()
    if existente:
        return existente

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

    if cuota_aceptada is not None:
        cuota_real = _aplicar_recotizacion(cuota, cuota_aceptada)
    else:
        cuota_real = cuota.valor

    asegurar_cuenta_usuario(usuario)
    id_apuesta = uuid.uuid4()
    clave_wallet = uuid.uuid4()

    ServicioBilletera.bloquear_para_apuesta(usuario, monto, id_apuesta, clave_wallet)

    apuesta = Apuesta.objects.create(
        usuario=usuario,
        tipo=TipoApuesta.SIMPLE,
        estado=EstadoApuesta.ACEPTADA,
        monto_apostado=monto,
        cuota_total=cuota_real,
        clave_idempotencia=clave_idempotencia,
        verificacion_juego_responsable=True,
        fecha_aceptacion=timezone.now(),
    )
    apuesta.calcular_ganancia_potencial()
    apuesta.save(update_fields=["ganancia_potencial"])

    PiernaApuesta.objects.create(
        apuesta=apuesta,
        cuota=cuota,
        cuota_al_momento=cuota_real,
    )

    apuesta._mensaje_juego = MENSAJE_CONSUMO_RESPONSABLE
    return apuesta


@transaction.atomic
def crear_apuesta_combinada(
    usuario,
    lista_cuotas: list,
    monto: Decimal,
    clave_idempotencia: str,
    acepto_juego_responsable: bool,
):
    existente = Apuesta.objects.filter(clave_idempotencia=clave_idempotencia).first()
    if existente:
        return existente

    if not acepto_juego_responsable:
        raise ValidationError("Debes confirmar el mensaje de consumo responsable.")

    perfil = getattr(usuario, "perfil", None)
    if perfil is None or not perfil.puede_apostar:
        raise ValidationError("Cuenta no habilitada para apostar (KYC o autoexclusión).")

    if monto < MONTO_MINIMO or monto > MONTO_MAXIMO:
        raise ValidationError(f"Monto fuera de rango ({MONTO_MINIMO} - {MONTO_MAXIMO}).")

    if len(lista_cuotas) < 2:
        raise ValidationError("La apuesta combinada requiere al menos 2 selecciones.")

    cuotas = []
    mercados_por_evento = set()
    for item in lista_cuotas:
        cuota_id = item.get("cuota_id")
        cuota_aceptada_str = item.get("cuota_aceptada")
        
        cuota = Cuota.objects.select_related("mercado__evento").get(pk=cuota_id)
        evento = cuota.mercado.evento
        mercado = cuota.mercado

        if evento.estado != EstadoEvento.PROGRAMADO:
            raise ValidationError(f"Evento '{evento.nombre}' no está programado.")

        if not evento.estan_apuestas_abiertas:
            raise ValidationError(f"Apuestas cerradas para '{evento.nombre}'.")

        if mercado.estado != EstadoMercado.ABIERTO or not cuota.activa:
            raise ValidationError(f"Mercado no disponible para '{evento.nombre}'.")

        clave = (evento.id, mercado.id)
        if clave in mercados_por_evento:
            raise ValidationError(f"Ya elegiste una cuota del mercado '{mercado.get_tipo_display()}' en '{evento.nombre}'.")
        mercados_por_evento.add(clave)

        if cuota_aceptada_str is not None:
            normalizado = str(cuota_aceptada_str).replace(",", ".")
            cuota_aceptada_val = Decimal(normalizado)
            cuota_real = _aplicar_recotizacion(cuota, cuota_aceptada_val)
        else:
            cuota_real = cuota.valor

        cuotas.append({"cuota": cuota, "cuota_real": cuota_real, "evento": evento})

    cuota_total = Decimal("1.0000")
    for item in cuotas:
        cuota_total *= item["cuota_real"]

    asegurar_cuenta_usuario(usuario)
    id_apuesta = uuid.uuid4()
    clave_wallet = uuid.uuid4()

    ServicioBilletera.bloquear_para_apuesta(usuario, monto, id_apuesta, clave_wallet)

    apuesta = Apuesta.objects.create(
        usuario=usuario,
        tipo=TipoApuesta.COMBINADA,
        estado=EstadoApuesta.ACEPTADA,
        monto_apostado=monto,
        cuota_total=cuota_total,
        clave_idempotencia=clave_idempotencia,
        verificacion_juego_responsable=True,
        fecha_aceptacion=timezone.now(),
    )
    apuesta.calcular_ganancia_potencial()
    apuesta.save(update_fields=["ganancia_potencial"])

    for item in cuotas:
        PiernaApuesta.objects.create(
            apuesta=apuesta,
            cuota=item["cuota"],
            cuota_al_momento=item["cuota_real"],
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

    for pierna in apuesta.piernas.all():
        pierna.es_ganadora = gano
        pierna.save(update_fields=["es_ganadora"])
        pierna.cuota.liquidar(es_ganadora=gano)

    return apuesta


def calcular_cash_out(apuesta_id) -> dict:
    apuesta = Apuesta.objects.get(pk=apuesta_id)
    if apuesta.estado != EstadoApuesta.ACEPTADA:
        raise ValidationError("Solo se puede calcular cash-out en apuestas aceptadas.")

    piernas = list(apuesta.piernas.all())
    if not piernas:
        raise ValidationError("La apuesta no tiene selecciones.")

    cuota_total_original = apuesta.cuota_total
    cuota_total_actual = Decimal("1.0000")
    evento_en_vivo = False

    for pierna in piernas:
        cuota_actual = pierna.cuota.valor
        cuota_total_actual *= cuota_actual
        if pierna.cuota.mercado.evento.estado == EstadoEvento.EN_VIVO:
            evento_en_vivo = True

    if cuota_total_actual <= 0:
        raise ValidationError("No se puede calcular cash-out con cuotas inválidas.")

    cash_out_bruto = apuesta.monto_apostado * cuota_total_original / cuota_total_actual
    cash_out_final = cash_out_bruto * (Decimal("1") - MARGEN_CASH_OUT)
    cash_out_final = max(cash_out_final, Decimal("0"))

    return {
        "apuesta_id": str(apuesta.id),
        "stake": apuesta.monto_apostado,
        "cuota_total_original": cuota_total_original,
        "cuota_total_actual": cuota_total_actual,
        "cash_out_bruto": cash_out_final.quantize(Decimal("0.0001")),
        "cash_out_final": cash_out_final.quantize(Decimal("0.0001")),
        "margen_aplicado": MARGEN_CASH_OUT,
        "en_vivo": evento_en_vivo,
    }


@transaction.atomic
def ejecutar_cash_out(apuesta_id):
    apuesta = Apuesta.objects.select_for_update().get(pk=apuesta_id)

    if apuesta.estado != EstadoApuesta.ACEPTADA:
        raise ValidationError("Solo puedes hacer cash-out de apuestas aceptadas.")

    if apuesta.monto_cash_out is not None:
        raise ValidationError("Esta apuesta ya tuvo cash-out.")

    calculo = calcular_cash_out(apuesta_id)
    monto_cash_out = calculo["cash_out_final"]

    if monto_cash_out <= 0:
        raise ValidationError("El cash-out no está disponible en este momento (valor cero o negativo).")

    clave = uuid.uuid4()
    ServicioBilletera.ejecutar_cash_out(
        apuesta.usuario,
        apuesta.monto_apostado,
        monto_cash_out,
        apuesta.id,
        clave,
    )

    apuesta.estado = EstadoApuesta.CASH_OUT
    apuesta.monto_cash_out = monto_cash_out
    apuesta.fecha_liquidacion = timezone.now()
    apuesta.save(update_fields=["estado", "monto_cash_out", "fecha_liquidacion"])

    return apuesta
