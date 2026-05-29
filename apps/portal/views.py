import uuid
from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from apps.users.models import PerfilUsuario
from apps.users.choices import EstadoKYC
from apps.wallet.models import (
    Cuenta, ServicioBilletera, asegurar_cuenta_usuario, asegurar_cuentas_sistema,
)
from apps.wallet.choices import TipoCuenta
from apps.events.models import Evento, Mercado, Cuota
from apps.events.choices import EstadoEvento, TipoMercado
from apps.betting.models import Apuesta
from apps.betting.services import crear_apuesta_simple, MONTO_MINIMO, MONTO_MAXIMO
from apps.responsible_gaming.helpers import crear_limites_por_defecto
from apps.responsible_gaming.models import LimiteDeposito, AutoExclusion
from apps.responsible_gaming.choices import TipoExclusion, PeriodoLimite
from apps.responsible_gaming.services import monto_recargado_en_periodo, validar_limite_recarga


def inicio(request):
    if request.user.is_authenticated:
        return redirect("portal-eventos")
    return render(request, "portal/inicio.html")


@require_http_methods(["GET", "POST"])
def registro(request):
    if request.user.is_authenticated:
        return redirect("portal-eventos")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        dni = request.POST.get("dni", "").strip()
        fecha = request.POST.get("fecha_nacimiento", "")

        if not all([username, password, dni, fecha]):
            messages.error(request, "Completa todos los campos.")
            return render(request, "portal/registro.html")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Ese usuario ya existe.")
            return render(request, "portal/registro.html")

        try:
            user = User.objects.create_user(username=username, password=password)
            PerfilUsuario.objects.create(
                usuario=user, dni=dni, fecha_nacimiento=fecha,
                estado_kyc=EstadoKYC.PENDIENTE,
            )
            asegurar_cuentas_sistema()
            asegurar_cuenta_usuario(user)
            crear_limites_por_defecto(user)
            messages.success(request, "Cuenta creada. Inicia sesión.")
            return redirect("portal-login")
        except ValidationError as e:
            messages.error(request, str(e))

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
        messages.error(request, "Usuario o contraseña incorrectos.")
    return render(request, "portal/login.html")


def cuenta_logout(request):
    logout(request)
    return redirect("portal-inicio")


@login_required
def perfil(request):
    perfil_u = request.user.perfil
    if request.method == "POST" and request.POST.get("accion") == "verificar_kyc":
        perfil_u.verificar()
        messages.success(request, "KYC verificado (simulado).")
        return redirect("portal-perfil")
    return render(request, "portal/perfil.html", {"perfil": perfil_u})


@login_required
def wallet(request):
    asegurar_cuenta_usuario(request.user)
    cuenta = Cuenta.objects.get(
        usuario=request.user, tipo_cuenta=TipoCuenta.BILLETERA_USUARIO
    )

    if request.method == "POST":
        accion = request.POST.get("accion")
        try:
            monto = Decimal(request.POST.get("monto", "0"))
        except (InvalidOperation, TypeError):
            messages.error(request, "Monto inválido.")
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


# =====================================================================
# 🛠️ VISTA DE EVENTOS ADAPTADA PARA EL NIVEL 2 POR NORVIL
# =====================================================================
@login_required
def eventos(request):
    # ✅ Forzamos la consulta directa de todos los eventos para que cargue sí o sí
    lista = Evento.objects.all().order_by("inicia_en").prefetch_related('mercados__cuotas')[:50]
    
    eventos_data = []
    
    # 2. Mapeamos de forma jerárquica: Evento -> Mercados -> Cuotas (Soporte Multi-Mercado N2)
    for ev in lista:
        mercados_lista = []
        for mer in ev.mercados.all():
            mercados_lista.append({
                "mercado": mer,
                "cuotas": list(mer.cuotas.filter(activa=True))
            })
            
        eventos_data.append({
            "evento": ev, 
            "mercados_con_cuotas": mercados_lista
        })

    # 3. Procesamiento seguro de apuestas mediante el formulario POST
    if request.method == "POST":
        cuota_id = request.POST.get("cuota_id")
        acepto = request.POST.get("acepto_juego_responsable")
        clave = request.POST.get("clave_idempotencia") or str(uuid.uuid4())

        if not acepto:
            messages.error(request, "Debes marcar el mensaje de juego responsable.")
            return redirect("portal-eventos")

        try:
            monto = Decimal(request.POST.get("monto", "0"))
        except (InvalidOperation, TypeError):
            messages.error(request, "Monto inválido.")
            return redirect("portal-eventos")

        try:
            apuesta = crear_apuesta_simple(
                request.user, cuota_id, monto, clave, True
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
        })

    exclusion = request.user.exclusiones.filter(activa=True).first()

    if request.method == "POST":
        accion = request.POST.get("accion")
        if accion == "limite":
            periodo = request.POST.get("periodo")
            try:
                monto = Decimal(request.POST.get("monto", "0"))
                limite, _ = LimiteDeposito.objects.get_or_create(
                    usuario=request.user, periodo=periodo, defaults={"monto": monto}
                )
                limite.actualizar_monto(monto)
                messages.success(request, "Límite actualizado.")
            except (ValidationError, InvalidOperation) as e:
                messages.error(request, str(e))
        elif accion == "exclusion":
            tipo = request.POST.get("tipo")
            if exclusion:
                messages.error(request, "Ya tienes una exclusión activa.")
            else:
                AutoExclusion.objects.create(usuario=request.user, tipo=tipo)
                messages.warning(request, "Autoexclusión activada.")
        return redirect("portal-responsable")

    return render(request, "portal/responsable.html", {
        "limites": limites,
        "exclusion": exclusion,
        "tipos_exclusion": TipoExclusion.choices,
        "periodos": PeriodoLimite.choices,
    })