import csv
import json
import uuid
from datetime import timedelta
from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Sum, Count
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from apps.betting.models import Apuesta
from apps.betting.choices import EstadoApuesta
from apps.betting.services import MONTO_MAXIMO, MONTO_MINIMO, crear_apuesta_simple, crear_apuesta_combinada, liquidar_apuesta
from apps.events.choices import EstadoEvento, TipoMercado, EstadoMercado, MotivoSuspension, CodigoSeleccion
from apps.events.models import Evento, Mercado, Cuota, HistorialCuota
from apps.responsible_gaming.choices import PeriodoLimite, TipoExclusion
from apps.responsible_gaming.helpers import crear_limites_por_defecto
from apps.responsible_gaming.models import AutoExclusion, LimiteDeposito, SuspiciousActivity
from apps.responsible_gaming.services import (
    monto_recargado_en_periodo,
    obtener_autoexclusion_vigente,
    validar_limite_recarga,
)
from apps.users.choices import EstadoKYC
from apps.users.models import PerfilUsuario
from apps.users.serializers import RegistroUsuarioSerializer
from apps.users.services import obtener_estado_operativo
from apps.wallet.choices import TipoCuenta, TipoAsiento, DireccionAsiento
from apps.wallet.models import (
    Cuenta,
    ServicioBilletera,
    asegurar_cuenta_usuario,
    asegurar_cuentas_sistema,
    AsientoContable,
)


Usuario = get_user_model()


def inicio(request):
    if request.user.is_authenticated:
        return redirect("portal-eventos")
    return render(request, "portal/inicio.html")


@require_http_methods(["GET", "POST"])
def registro(request):
    if request.user.is_authenticated:
        return redirect("portal-eventos")

    if request.method == "POST":
        datos = {
            "username": request.POST.get("username", "").strip(),
            "password": request.POST.get("password", ""),
            "dni": request.POST.get("dni", "").strip(),
            "fecha_nacimiento": request.POST.get("fecha_nacimiento", ""),
        }
        serializer = RegistroUsuarioSerializer(data=datos)

        if not serializer.is_valid():
            for campo, errores in serializer.errors.items():
                mensajes = " ".join(str(error) for error in errores)
                messages.error(request, f"{campo}: {mensajes}")
            return render(request, "portal/registro.html")

        datos_validados = serializer.validated_data

        with transaction.atomic():
            user = Usuario.objects.create_user(
                username=datos_validados["username"],
                password=datos_validados["password"],
            )
            PerfilUsuario.objects.create(
                usuario=user,
                dni=datos_validados["dni"],
                fecha_nacimiento=datos_validados["fecha_nacimiento"],
                estado_kyc=EstadoKYC.PENDIENTE,
            )
            asegurar_cuentas_sistema()
            asegurar_cuenta_usuario(user)
            crear_limites_por_defecto(user)
            messages.success(request, "Cuenta creada. Inicia sesion.")
            return redirect("portal-login")

    return render(request, "portal/registro.html")


@require_http_methods(["GET", "POST"])
def cuenta_login(request):
    if request.method == "POST":
        user = authenticate(
            request,
            username=request.POST.get("username"),
            password=request.POST.get("password"),
        )
        if user:
            login(request, user)
            return redirect("portal-eventos")
        messages.error(request, "Usuario o contrasena incorrectos.")
    return render(request, "portal/login.html")


def cuenta_logout(request):
    logout(request)
    return redirect("portal-inicio")


@login_required
def perfil(request):
    perfil_u = request.user.perfil
    estado_operativo = obtener_estado_operativo(request.user)
    if request.method == "POST" and request.POST.get("accion") == "verificar_kyc":
        perfil_u.verificar()
        messages.success(request, "KYC verificado (simulado).")
        return redirect("portal-perfil")
    return render(request, "portal/perfil.html", {
        "perfil": perfil_u,
        "estado_operativo": estado_operativo,
    })


@login_required
def wallet(request):
    asegurar_cuenta_usuario(request.user)
    cuenta = Cuenta.objects.get(
        usuario=request.user,
        tipo_cuenta=TipoCuenta.BILLETERA_USUARIO,
    )

    if request.method == "POST":
        accion = request.POST.get("accion")
        try:
            monto = Decimal(request.POST.get("monto", "0"))
        except (InvalidOperation, TypeError):
            messages.error(request, "Monto invalido.")
            return redirect("portal-wallet")

        clave = uuid.uuid4()
        asegurar_cuentas_sistema()
        try:
            if accion == "recarga":
                validar_limite_recarga(request.user, monto)
                ServicioBilletera.recargar(request.user, monto, clave)
                messages.success(request, f"Recarga de {monto} FIC ok.")
            elif accion == "retiro":
                ServicioBilletera.retirar(request.user, monto, clave)
                messages.success(request, f"Retiro de {monto} FIC ok.")
            elif accion == "transferir":
                destino = request.POST.get("usuario_destino", "").strip()
                ServicioBilletera.transferir(request.user, destino, monto, clave)
                messages.success(request, f"Transferiste {monto} FIC a {destino}.")
        except ValidationError as e:
            messages.error(request, str(e))
        return redirect("portal-wallet")

    cuenta.refresh_from_db()
    return render(request, "portal/wallet.html", {"cuenta": cuenta})


@login_required
def eventos(request):
    estado_operativo = obtener_estado_operativo(request.user)
    lista = Evento.objects.filter(estado=EstadoEvento.PROGRAMADO).order_by("inicia_en")
    eventos_data = []
    for ev in lista:
        mercados_con_cuotas = []
        for m in ev.mercados.filter(estado=EstadoMercado.ABIERTO).prefetch_related("cuotas"):
            cuotas_activas = list(m.cuotas.filter(activa=True))
            if cuotas_activas:
                mercados_con_cuotas.append({"mercado": m, "cuotas": cuotas_activas})
        eventos_data.append({"evento": ev, "mercados_con_cuotas": mercados_con_cuotas})

    if request.method == "POST":
        if not estado_operativo["puede_apostar"]:
            messages.error(request, estado_operativo["motivo"])
            return redirect("portal-eventos")

        tipo = request.POST.get("tipo_apuesta", "simple")
        acepto = request.POST.get("acepto_juego_responsable")
        clave = request.POST.get("clave_idempotencia") or str(uuid.uuid4())

        if not acepto:
            messages.error(request, "Debes marcar el mensaje de juego responsable.")
            return redirect("portal-eventos")

        try:
            monto = Decimal(request.POST.get("monto", "0"))
        except (InvalidOperation, TypeError):
            messages.error(request, "Monto invalido.")
            return redirect("portal-eventos")

        try:
            if tipo == "combinada":
                raw = request.POST.get("selecciones_json", "[]")
                selecciones = json.loads(raw)
                apuesta = crear_apuesta_combinada(
                    request.user, selecciones, monto, clave, True,
                )
            else:
                cuota_id = request.POST.get("cuota_id")
                apuesta = crear_apuesta_simple(
                    request.user, cuota_id, monto, clave, True,
                )
            messages.success(
                request,
                f"Apuesta {'combinada' if tipo == 'combinada' else 'simple'} aceptada. Ganancia potencial: {apuesta.ganancia_potencial} FIC",
            )
            return redirect("portal-apuestas")
        except (ValidationError, json.JSONDecodeError) as e:
            messages.error(request, str(e))

    return render(request, "portal/eventos.html", {
        "eventos_data": eventos_data,
        "monto_min": MONTO_MINIMO,
        "monto_max": MONTO_MAXIMO,
        "estado_operativo": estado_operativo,
    })


@login_required
def apuestas(request):
    lista = Apuesta.objects.filter(usuario=request.user).order_by("-fecha_creacion")
    return render(request, "portal/apuestas.html", {"apuestas": lista})


@login_required
def juego_responsable(request):
    limites = []
    for lim in LimiteDeposito.objects.filter(usuario=request.user):
        limites.append({
            "obj": lim,
            "usado": monto_recargado_en_periodo(request.user, lim.periodo),
            "puede_aplicar_pendiente": lim.puede_aplicar_aumento_pendiente(),
        })

    exclusion = obtener_autoexclusion_vigente(request.user)

    if request.method == "POST":
        accion = request.POST.get("accion")
        if accion == "limite":
            periodo = request.POST.get("periodo")
            try:
                monto = Decimal(request.POST.get("monto", "0"))
                limite, _ = LimiteDeposito.objects.get_or_create(
                    usuario=request.user,
                    periodo=periodo,
                    defaults={"monto": monto},
                )
                monto_anterior = limite.monto
                limite.actualizar_monto(monto)
                if monto > monto_anterior:
                    messages.success(
                        request,
                        "Aumento registrado como pendiente por 24 horas.",
                    )
                else:
                    messages.success(request, "Limite actualizado.")
            except (ValidationError, InvalidOperation) as e:
                messages.error(request, str(e))
        elif accion == "aplicar_limite_pendiente":
            periodo = request.POST.get("periodo")
            try:
                limite = LimiteDeposito.objects.get(
                    usuario=request.user,
                    periodo=periodo,
                )
                limite.aplicar_aumento_pendiente()
                messages.success(request, "Aumento pendiente aplicado.")
            except (LimiteDeposito.DoesNotExist, ValidationError) as e:
                messages.error(request, str(e))
        elif accion == "exclusion":
            tipo = request.POST.get("tipo")
            if obtener_autoexclusion_vigente(request.user):
                messages.error(request, "Ya tienes una exclusion activa.")
            else:
                AutoExclusion.objects.create(usuario=request.user, tipo=tipo)
                messages.warning(request, "Autoexclusion activada.")
        return redirect("portal-responsable")

    return render(request, "portal/responsable.html", {
        "limites": limites,
        "exclusion": exclusion,
        "tipos_exclusion": TipoExclusion.choices,
        "periodos": PeriodoLimite.choices,
    })


# ─── Operador ─────────────────────────────────────────────

def _es_operador(user):
    return user.is_authenticated and user.is_staff


@user_passes_test(_es_operador, login_url="/cuenta/login/")
def operador_dashboard(request):
    ahora = timezone.now()
    hoy_inicio = ahora.replace(hour=0, minute=0, second=0, microsecond=0)
    ultimas_24h = ahora - timedelta(hours=24)

    ganancias_casa = AsientoContable.objects.filter(
        tipo_asiento=TipoAsiento.PERDIDA_APUESTA,
        direccion=DireccionAsiento.CREDITO,
        fecha_creacion__gte=hoy_inicio,
    ).aggregate(s=Sum("monto"))["s"] or 0

    perdidas_casa = AsientoContable.objects.filter(
        tipo_asiento=TipoAsiento.GANANCIA_APUESTA,
        direccion=DireccionAsiento.DEBITO,
        fecha_creacion__gte=hoy_inicio,
    ).aggregate(s=Sum("monto"))["s"] or 0

    ggr = ganancias_casa - perdidas_casa

    apuestas_activas = Apuesta.objects.filter(estado=EstadoApuesta.ACEPTADA)
    exposure = apuestas_activas.aggregate(s=Sum("monto_apostado"))["s"] or 0

    apuestas_hoy = Apuesta.objects.filter(fecha_creacion__gte=hoy_inicio)
    volumen = {
        "cantidad": apuestas_hoy.count(),
        "monto_total": str(apuestas_hoy.aggregate(s=Sum("monto_apostado"))["s"] or 0),
    }

    usuarios_activos_24h = Apuesta.objects.filter(
        fecha_creacion__gte=ultimas_24h,
    ).values("usuario").distinct().count()

    alertas_pendientes = SuspiciousActivity.objects.filter(estado="pendiente").count()
    total_usuarios = Usuario.objects.count()

    return render(request, "operador/dashboard.html", {
        "ggr": str(ggr),
        "exposure": str(exposure),
        "volumen": volumen,
        "apuestas_hoy": apuestas_hoy.count(),
        "usuarios_activos_24h": usuarios_activos_24h,
        "total_usuarios": total_usuarios,
        "alertas_pendientes": alertas_pendientes,
        "fecha_actualizacion": ahora,
    })


@user_passes_test(_es_operador, login_url="/cuenta/login/")
def operador_eventos(request):
    if request.method == "POST":
        accion = request.POST.get("accion")

        if accion == "crear":
            nombre = request.POST.get("nombre", "").strip()
            local = request.POST.get("equipo_local", "").strip()
            visitante = request.POST.get("equipo_visitante", "").strip()
            inicia = request.POST.get("inicia_en")
            if nombre and local and visitante and inicia:
                Evento.objects.create(
                    nombre=nombre, equipo_local=local, equipo_visitante=visitante,
                    inicia_en=inicia,
                )
                messages.success(request, "Evento creado.")
            else:
                messages.error(request, "Faltan campos obligatorios.")

        elif accion == "cambiar_estado":
            evento_id = request.POST.get("evento_id")
            estado = request.POST.get("estado")
            if evento_id and estado:
                try:
                    e = Evento.objects.get(pk=evento_id)
                    e.estado = estado
                    e.ultimo_cambio_estado = timezone.now()
                    e.save(update_fields=["estado", "ultimo_cambio_estado"])
                    messages.success(request, f"Evento cambiado a {estado}.")
                except Evento.DoesNotExist:
                    messages.error(request, "Evento no encontrado.")

        elif accion == "marcar_resultado":
            evento_id = request.POST.get("evento_id")
            try:
                goles_local = int(request.POST.get("goles_local", 0))
                goles_visitante = int(request.POST.get("goles_visitante", 0))
                e = Evento.objects.get(pk=evento_id)
                e.resultado = {"local": goles_local, "visitante": goles_visitante}
                e.save(update_fields=["resultado"])
                messages.success(request, "Resultado registrado.")
            except (Evento.DoesNotExist, ValueError):
                messages.error(request, "Error al marcar resultado.")

        elif accion == "suspender_mercado":
            mercado_id = request.POST.get("mercado_id")
            segundos = request.POST.get("segundos")
            try:
                m = Mercado.objects.get(pk=mercado_id)
                m.suspender(
                    motivo=MotivoSuspension.MANUAL,
                    segundos=int(segundos) if segundos else None,
                )
                messages.success(request, "Mercado suspendido.")
            except Mercado.DoesNotExist:
                messages.error(request, "Mercado no encontrado.")

        elif accion == "reabrir_mercado":
            mercado_id = request.POST.get("mercado_id")
            try:
                m = Mercado.objects.get(pk=mercado_id)
                m.reabrir()
                messages.success(request, "Mercado reabierto.")
            except Mercado.DoesNotExist:
                messages.error(request, "Mercado no encontrado.")

        elif accion == "actualizar_cuota":
            cuota_id = request.POST.get("cuota_id")
            try:
                valor = Decimal(str(request.POST.get("valor", "0")))
                if valor <= 0:
                    raise ValueError
                c = Cuota.objects.get(pk=cuota_id)
                HistorialCuota.objects.create(cuota=c, valor=c.valor)
                c.valor = valor
                c.save(update_fields=["valor"])
                messages.success(request, "Cuota actualizada.")
            except (Cuota.DoesNotExist, ValueError):
                messages.error(request, "Error al actualizar cuota.")

        return redirect("operador-eventos")

    eventos = Evento.objects.prefetch_related("mercados__cuotas").all().order_by("-inicia_en")
    return render(request, "operador/eventos.html", {"eventos": eventos})


@user_passes_test(_es_operador, login_url="/cuenta/login/")
def operador_apuestas(request):
    if request.method == "POST":
        apuesta_id = request.POST.get("apuesta_id")
        gano = request.POST.get("gano") == "true"
        try:
            liquidar_apuesta(apuesta_id, gano)
            messages.success(request, f"Apuesta liquidada como {'ganada' if gano else 'perdida'}.")
        except ValidationError as e:
            messages.error(request, str(e))
        return redirect("operador-apuestas")

    apuestas = Apuesta.objects.select_related("usuario").all().order_by("-fecha_creacion")
    return render(request, "operador/apuestas.html", {"apuestas": apuestas})


@user_passes_test(_es_operador, login_url="/cuenta/login/")
def operador_alertas(request):
    if request.method == "POST":
        alerta_id = request.POST.get("alerta_id")
        estado = request.POST.get("estado")
        try:
            a = SuspiciousActivity.objects.get(pk=alerta_id)
            a.estado = estado
            a.save(update_fields=["estado"])
            messages.success(request, f"Alerta marcada como {estado}.")
        except SuspiciousActivity.DoesNotExist:
            messages.error(request, "Alerta no encontrada.")
        return redirect("operador-alertas")

    estado_filtro = request.GET.get("estado")
    alertas = SuspiciousActivity.objects.select_related("usuario").all().order_by("-fecha_creacion")
    if estado_filtro:
        alertas = alertas.filter(estado=estado_filtro)
    return render(request, "operador/alertas.html", {"alertas": alertas})


@user_passes_test(_es_operador, login_url="/cuenta/login/")
def operador_reporte(request):
    ahora = timezone.now()
    inicio_mes = ahora.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    apuestas = Apuesta.objects.filter(
        fecha_creacion__gte=inicio_mes,
    ).select_related("usuario").order_by("fecha_creacion")

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f"attachment; filename=reporte-mensual-{ahora.strftime('%Y-%m')}.csv"

    writer = csv.writer(response)
    writer.writerow([
        "Fecha", "Usuario", "Tipo", "Estado", "Monto Apostado",
        "Cuota", "Ganancia Potencial", "Ganancia Real",
    ])

    for a in apuestas:
        writer.writerow([
            a.fecha_creacion.strftime("%Y-%m-%d %H:%M:%S"),
            a.usuario.username,
            a.tipo,
            a.estado,
            str(a.monto_apostado),
            str(a.cuota_total),
            str(a.ganancia_potencial),
            str(a.ganancia_real) if a.ganancia_real is not None else "",
        ])

    return response
