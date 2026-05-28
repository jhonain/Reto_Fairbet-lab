import uuid
from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from apps.betting.models import Apuesta
from apps.betting.services import MONTO_MAXIMO, MONTO_MINIMO, crear_apuesta_simple
from apps.events.choices import EstadoEvento, TipoMercado
from apps.events.models import Evento
from apps.responsible_gaming.choices import PeriodoLimite, TipoExclusion
from apps.responsible_gaming.helpers import crear_limites_por_defecto
from apps.responsible_gaming.models import AutoExclusion, LimiteDeposito
from apps.responsible_gaming.services import (
    monto_recargado_en_periodo,
    obtener_autoexclusion_vigente,
    validar_limite_recarga,
)
from apps.users.choices import EstadoKYC
from apps.users.models import PerfilUsuario
from apps.users.serializers import RegistroUsuarioSerializer
from apps.users.services import obtener_estado_operativo
from apps.wallet.choices import TipoCuenta
from apps.wallet.models import (
    Cuenta,
    ServicioBilletera,
    asegurar_cuenta_usuario,
    asegurar_cuentas_sistema,
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
        mercado = ev.mercados.filter(tipo=TipoMercado.UNO_X_DOS).first()
        cuotas = list(mercado.cuotas.filter(activa=True)) if mercado else []
        eventos_data.append({"evento": ev, "cuotas": cuotas})

    if request.method == "POST":
        if not estado_operativo["puede_apostar"]:
            messages.error(request, estado_operativo["motivo"])
            return redirect("portal-eventos")

        cuota_id = request.POST.get("cuota_id")
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
            apuesta = crear_apuesta_simple(
                request.user,
                cuota_id,
                monto,
                clave,
                True,
            )
            messages.success(
                request,
                f"Apuesta aceptada. Ganancia potencial: {apuesta.ganancia_potencial} FIC",
            )
            return redirect("portal-apuestas")
        except ValidationError as e:
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
