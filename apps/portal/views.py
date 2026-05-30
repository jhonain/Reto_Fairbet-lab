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
from apps.betting.choices import EstadoApuesta
from apps.betting.services import MONTO_MAXIMO, MONTO_MINIMO, crear_apuesta_simple, crear_apuesta_combinada, hacer_cash_out, calcular_cash_out
from apps.events.choices import EstadoEvento, TipoMercado
from apps.events.models import Evento, Cuota
from apps.responsible_gaming.choices import PeriodoLimite, TipoExclusion
from apps.responsible_gaming.helpers import crear_limites_por_defecto
from apps.responsible_gaming.models import AutoExclusion, LimiteDeposito
from apps.responsible_gaming.services import monto_recargado_en_periodo, obtener_autoexclusion_vigente, registrar_alerta_multiples_cuentas_ip, validar_limite_recarga
from apps.users.choices import EstadoKYC
from apps.users.models import PerfilUsuario
from apps.users.serializers import RegistroUsuarioSerializer
from apps.users.services import obtener_estado_operativo
from apps.wallet.choices import TipoCuenta
from apps.wallet.models import Cuenta, ServicioBilletera, asegurar_cuenta_usuario, asegurar_cuentas_sistema
Usuario = get_user_model()

def obtener_ip(request):
    adelante = request.META.get('HTTP_X_FORWARDED_FOR')
    if adelante:
        return adelante.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')

def inicio(request):
    if request.user.is_authenticated:
        return redirect('portal-eventos')
    return render(request, 'portal/inicio.html')

@require_http_methods(['GET', 'POST'])
def registro(request):
    if request.user.is_authenticated:
        return redirect('portal-eventos')
    if request.method == 'POST':
        datos = {'username': request.POST.get('username', '').strip(), 'password': request.POST.get('password', ''), 'dni': request.POST.get('dni', '').strip(), 'fecha_nacimiento': request.POST.get('fecha_nacimiento', '')}
        serializer = RegistroUsuarioSerializer(data=datos)
        if not serializer.is_valid():
            for campo, errores in serializer.errors.items():
                mensajes = ' '.join((str(error) for error in errores))
                messages.error(request, f'{campo}: {mensajes}')
            return render(request, 'portal/registro.html')
        datos_validados = serializer.validated_data
        ip = obtener_ip(request)
        with transaction.atomic():
            user = Usuario.objects.create_user(username=datos_validados['username'], password=datos_validados['password'])
            PerfilUsuario.objects.create(usuario=user, dni=datos_validados['dni'], fecha_nacimiento=datos_validados['fecha_nacimiento'], estado_kyc=EstadoKYC.PENDIENTE)
            asegurar_cuentas_sistema()
            asegurar_cuenta_usuario(user)
            crear_limites_por_defecto(user)
            registrar_alerta_multiples_cuentas_ip(user, ip)
            messages.success(request, 'Cuenta creada. Inicia sesion.')
            return redirect('portal-login')
    return render(request, 'portal/registro.html')

@require_http_methods(['GET', 'POST'])
def cuenta_login(request):
    if request.method == 'POST':
        user = authenticate(request, username=request.POST.get('username'), password=request.POST.get('password'))
        if user:
            login(request, user)
            return redirect('portal-eventos')
        messages.error(request, 'Usuario o contrasena incorrectos.')
    return render(request, 'portal/login.html')

def cuenta_logout(request):
    logout(request)
    return redirect('portal-inicio')

@login_required
def perfil(request):
    perfil_u = request.user.perfil
    estado_operativo = obtener_estado_operativo(request.user)
    if request.method == 'POST' and request.POST.get('accion') == 'verificar_kyc':
        perfil_u.verificar()
        messages.success(request, 'KYC verificado (simulado).')
        return redirect('portal-perfil')
    return render(request, 'portal/perfil.html', {'perfil': perfil_u, 'estado_operativo': estado_operativo})


@login_required
def wallet(request):
    asegurar_cuenta_usuario(request.user)
    cuenta = Cuenta.objects.get(usuario=request.user, tipo_cuenta=TipoCuenta.BILLETERA_USUARIO)

    if request.method == 'POST':
        accion = request.POST.get('accion')

        try:
            monto = Decimal(request.POST.get('monto', '0'))
        except (InvalidOperation, TypeError):
            messages.error(request, 'Monto invalido.')
            return redirect('portal-wallet')

        if monto <= 0:
            messages.error(request, 'El monto debe ser mayor a cero.')
            return redirect('portal-wallet')

        clave = uuid.uuid4()
        asegurar_cuentas_sistema()

        try:
            if accion == 'recarga':
                validar_limite_recarga(request.user, monto)
                ServicioBilletera.recargar(request.user, monto, clave)
                messages.success(request, f'Recarga de {monto} FIC ok.')

            elif accion == 'retiro':
                ServicioBilletera.retirar(request.user, monto, clave)
                messages.success(request, f'Retiro de {monto} FIC ok.')

            elif accion == 'transferir':
                destino = request.POST.get('usuario_destino', '').strip()

                if not destino:
                    messages.error(request, 'Debes ingresar el usuario destino.')
                    return redirect('portal-wallet')

                if destino == request.user.username:
                    messages.error(request, 'No puedes transferirte fichas a ti mismo.')
                    return redirect('portal-wallet')

                existe_destino = Cuenta.objects.filter(
                    usuario__username=destino,
                    tipo_cuenta=TipoCuenta.BILLETERA_USUARIO,
                ).exists()

                if not existe_destino:
                    messages.error(request, 'El usuario destino no existe.')
                    return redirect('portal-wallet')

                ServicioBilletera.transferir(request.user, destino, monto, clave)
                messages.success(request, f'Transferiste {monto} FIC a {destino}.')

        except ValidationError as e:
            messages.error(request, str(e))

        return redirect('portal-wallet')

    cuenta.refresh_from_db()
    return render(request, 'portal/wallet.html', {'cuenta': cuenta})

@login_required
def eventos(request):
    estado_operativo = obtener_estado_operativo(request.user)
    lista = Evento.objects.filter(estado=EstadoEvento.PROGRAMADO).order_by('inicia_en')
    eventos_data = []
    for ev in lista:
        mercados_con_cuotas = []
        for mercado in ev.mercados.all().order_by('tipo'):
            mercados_con_cuotas.append({'mercado': mercado, 'cuotas': list(mercado.cuotas.filter(activa=True))})
        eventos_data.append({'evento': ev, 'mercados_con_cuotas': mercados_con_cuotas})
    if request.method == 'POST':
        if not estado_operativo['puede_apostar']:
            messages.error(request, estado_operativo['motivo'])
            return redirect('portal-eventos')
        cuota_id = request.POST.get('cuota_id')
        acepto = request.POST.get('acepto_juego_responsable')
        clave = request.POST.get('clave_idempotencia') or str(uuid.uuid4())
        if not acepto:
            messages.error(request, 'Debes marcar el mensaje de juego responsable.')
            return redirect('portal-eventos')
        try:
            monto = Decimal(request.POST.get('monto', '0'))
        except (InvalidOperation, TypeError):
            messages.error(request, 'Monto invalido.')
            return redirect('portal-eventos')
        try:
            apuesta = crear_apuesta_simple(request.user, cuota_id, monto, clave, True)
            messages.success(request, f'Apuesta aceptada. Ganancia potencial: {apuesta.ganancia_potencial} FIC')
            return redirect('portal-apuestas')
        except ValidationError as e:
            messages.error(request, str(e))
    return render(request, 'portal/eventos.html', {'eventos_data': eventos_data, 'monto_min': MONTO_MINIMO, 'monto_max': MONTO_MAXIMO, 'estado_operativo': estado_operativo})

@login_required
def combinada(request):
    estado_operativo = obtener_estado_operativo(request.user)
    lista = Evento.objects.filter(estado=EstadoEvento.PROGRAMADO).order_by('inicia_en')
    eventos_data = []
    for ev in lista:
        mercado = ev.mercados.filter(tipo=TipoMercado.UNO_X_DOS).first()
        cuotas = list(mercado.cuotas.filter(activa=True)) if mercado else []
        eventos_data.append({'evento': ev, 'cuotas': cuotas})
    if request.method == 'POST':
        if not estado_operativo['puede_apostar']:
            messages.error(request, estado_operativo['motivo'])
            return redirect('portal-combinada')
        if not request.POST.get('acepto_juego_responsable'):
            messages.error(request, 'Debes marcar el mensaje de juego responsable.')
            return redirect('portal-combinada')
        cuota_ids = request.POST.getlist('cuota_ids')
        clave = str(uuid.uuid4())
        try:
            monto = Decimal(request.POST.get('monto', '0'))
        except (InvalidOperation, TypeError):
            messages.error(request, 'Monto invalido.')
            return redirect('portal-combinada')
        try:
            apuesta = crear_apuesta_combinada(request.user, cuota_ids, monto, clave, True)
            messages.success(request, f'Combinada aceptada. Cuota total: {apuesta.cuota_total} | Ganancia potencial: {apuesta.ganancia_potencial} FIC')
            return redirect('portal-apuestas')
        except ValidationError as e:
            messages.error(request, str(e))
    return render(request, 'portal/combinada.html', {'eventos_data': eventos_data, 'monto_min': MONTO_MINIMO, 'monto_max': MONTO_MAXIMO, 'estado_operativo': estado_operativo})

@login_required
def apuestas(request):
    if request.method == 'POST' and request.POST.get('accion') == 'cash_out':
        apuesta_id = request.POST.get('apuesta_id')
        try:
            apuesta = Apuesta.objects.get(id=apuesta_id, usuario=request.user)
            hacer_cash_out(apuesta.id)
            apuesta.refresh_from_db()
            messages.success(request, f'Cash-out realizado: {apuesta.monto_cash_out} FIC.')
        except Apuesta.DoesNotExist:
            messages.error(request, 'Apuesta no encontrada.')
        except ValidationError as e:
            messages.error(request, str(e))
        return redirect('portal-apuestas')
    lista = Apuesta.objects.filter(usuario=request.user).order_by('-fecha_creacion')
    apuestas_data = []
    for a in lista:
        estimado = calcular_cash_out(a) if a.estado == EstadoApuesta.ACEPTADA else None
        apuestas_data.append({'apuesta': a, 'cash_out_estimado': estimado})
    return render(request, 'portal/apuestas.html', {'apuestas_data': apuestas_data})

@login_required
def juego_responsable(request):
    crear_limites_por_defecto(request.user)
    limites = []
    for lim in LimiteDeposito.objects.filter(usuario=request.user):
        limites.append({'obj': lim, 'usado': monto_recargado_en_periodo(request.user, lim.periodo), 'puede_aplicar_pendiente': lim.puede_aplicar_aumento_pendiente()})
    exclusion = obtener_autoexclusion_vigente(request.user)
    if request.method == 'POST':
        accion = request.POST.get('accion')
        if accion == 'limite':
            periodo = request.POST.get('periodo')
            try:
                monto = Decimal(request.POST.get('monto', '0'))
                limite, _ = LimiteDeposito.objects.get_or_create(usuario=request.user, periodo=periodo, defaults={'monto': monto})
                monto_anterior = limite.monto
                limite.actualizar_monto(monto)
                if monto > monto_anterior:
                    messages.success(request, 'Aumento registrado como pendiente por 24 horas.')
                else:
                    messages.success(request, 'Limite actualizado.')
            except (ValidationError, InvalidOperation) as e:
                messages.error(request, str(e))
        elif accion == 'aplicar_limite_pendiente':
            periodo = request.POST.get('periodo')
            try:
                limite = LimiteDeposito.objects.get(usuario=request.user, periodo=periodo)
                limite.aplicar_aumento_pendiente()
                messages.success(request, 'Aumento pendiente aplicado.')
            except (LimiteDeposito.DoesNotExist, ValidationError) as e:
                messages.error(request, str(e))
        elif accion == 'exclusion':
            tipo = request.POST.get('tipo')
            if obtener_autoexclusion_vigente(request.user):
                messages.error(request, 'Ya tienes una exclusion activa.')
            else:
                AutoExclusion.objects.create(usuario=request.user, tipo=tipo)
                messages.warning(request, 'Autoexclusion activada.')
        return redirect('portal-responsable')
    return render(request, 'portal/responsable.html', {'limites': limites, 'exclusion': exclusion, 'tipos_exclusion': TipoExclusion.choices, 'periodos': PeriodoLimite.choices})