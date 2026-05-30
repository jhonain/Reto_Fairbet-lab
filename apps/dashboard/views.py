import csv
from decimal import Decimal, InvalidOperation
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import ValidationError
from django.db.models import Sum
from django.db.models.deletion import ProtectedError
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from apps.betting.models import Apuesta
from apps.betting.choices import EstadoApuesta
from apps.betting.services import liquidar_apuesta
from apps.responsible_gaming.models import LimiteDeposito
from apps.responsible_gaming.services import monto_recargado_en_periodo
from apps.events.models import Evento, Mercado, Cuota
from apps.events.choices import EstadoEvento, TipoMercado, CodigoSeleccion
from apps.responsible_gaming.models import SuspiciousActivity
from .services import verificar_integridad

def es_operador(user):
    return user.is_authenticated and user.is_staff

def ejecutar_accion_sobre_evento(request, evento, accion):
    if accion == 'simular_critico':
        evento.suspender_por_evento_critico(30)
        messages.success(request, 'Mercados suspendidos por 30 segundos: ' + str(evento))
        return 'detalle'
    if accion == 'eliminar':
        try:
            Cuota.objects.filter(mercado__evento=evento).delete()
            Mercado.objects.filter(evento=evento).delete()
            evento.delete()
            messages.success(request, 'Evento eliminado.')
        except ProtectedError:
            messages.error(request, 'No se puede eliminar: tiene apuestas asociadas.')
        return 'lista'
    estados_validos = {'estado_programado': EstadoEvento.PROGRAMADO, 'estado_en_vivo': EstadoEvento.EN_VIVO, 'estado_finalizado': EstadoEvento.FINALIZADO, 'estado_suspendido': EstadoEvento.SUSPENDIDO, 'estado_anulado': EstadoEvento.ANULADO}
    if accion in estados_validos:
        evento.estado = estados_validos[accion]
        evento.save(update_fields=['estado'])
        messages.success(request, 'Estado actualizado a: ' + evento.get_estado_display())
        return 'detalle'
    messages.error(request, 'Acción no válida.')
    return 'detalle'

def crear_mercados_por_defecto(evento):
    m_1x2, _ = Mercado.objects.get_or_create(evento=evento, tipo=TipoMercado.UNO_X_DOS, defaults={'margen_operador': Decimal('0.0500')})
    for sel, valor in [(CodigoSeleccion.LOCAL, Decimal('2.1000')), (CodigoSeleccion.EMPATE, Decimal('3.2000')), (CodigoSeleccion.VISITANTE, Decimal('3.5000'))]:
        Cuota.objects.update_or_create(mercado=m_1x2, seleccion=sel, defaults={'valor': valor, 'activa': True})
    m_ou, _ = Mercado.objects.get_or_create(evento=evento, tipo=TipoMercado.SOBRE_BAJO, defaults={'margen_operador': Decimal('0.0500')})
    for sel, valor in [(CodigoSeleccion.SOBRE, Decimal('1.9000')), (CodigoSeleccion.BAJO, Decimal('1.8000'))]:
        Cuota.objects.update_or_create(mercado=m_ou, seleccion=sel, defaults={'valor': valor, 'activa': True})
    m_btts, _ = Mercado.objects.get_or_create(evento=evento, tipo=TipoMercado.AMBOS_ANOTAN, defaults={'margen_operador': Decimal('0.0500')})
    for sel, valor in [(CodigoSeleccion.SI, Decimal('1.7000')), (CodigoSeleccion.NO, Decimal('2.0000'))]:
        Cuota.objects.update_or_create(mercado=m_btts, seleccion=sel, defaults={'valor': valor, 'activa': True})

def _suma(qs, campo):
    return qs.aggregate(total=Sum(campo))['total'] or Decimal('0')

@login_required
@user_passes_test(es_operador)
def panel_operador(request):
    liquidadas = Apuesta.objects.filter(estado__in=[EstadoApuesta.GANADA, EstadoApuesta.PERDIDA, EstadoApuesta.CASH_OUT])
    pendientes = Apuesta.objects.filter(estado=EstadoApuesta.ACEPTADA)
    stakes_liquidadas = _suma(liquidadas, 'monto_apostado')
    payouts = _suma(liquidadas, 'ganancia_real')
    ggr = stakes_liquidadas - payouts
    exposicion = _suma(pendientes, 'ganancia_potencial')
    integridad_ok, integridad_msg = verificar_integridad()
    context = {'ggr': ggr, 'exposicion': exposicion, 'volumen_total': Apuesta.objects.count(), 'volumen_pendiente': pendientes.count(), 'usuarios_activos': Apuesta.objects.values('usuario').distinct().count(), 'alertas': SuspiciousActivity.objects.filter(regla='multiples_cuentas_ip', estado='pendiente').order_by('-fecha_creacion')[:20], 'integridad_ok': integridad_ok, 'integridad_msg': integridad_msg}
    return render(request, 'dashboard/panel.html', context)

@login_required
@user_passes_test(es_operador)
def gestion_eventos(request):
    if request.method == 'POST':
        accion = request.POST.get('accion')
        evento_id = request.POST.get('evento_id')
        if accion and evento_id:
            evento = get_object_or_404(Evento, pk=evento_id)
            destino = ejecutar_accion_sobre_evento(request, evento, accion)
            if destino == 'lista':
                return redirect('dashboard-eventos')
            return redirect('dashboard-evento-detalle', evento_id=evento_id)
        nombre = request.POST.get('nombre', '').strip()
        local = request.POST.get('equipo_local', '').strip()
        visitante = request.POST.get('equipo_visitante', '').strip()
        inicia_en = request.POST.get('inicia_en', '').strip()
        if not local or not visitante or (not inicia_en):
            messages.error(request, 'Completa local, visitante y la fecha de inicio.')
            return redirect('dashboard-eventos')
        fecha = parse_datetime(inicia_en)
        if fecha is None:
            messages.error(request, 'La fecha de inicio no es valida.')
            return redirect('dashboard-eventos')
        if timezone.is_naive(fecha):
            fecha = timezone.make_aware(fecha)
        if not nombre:
            nombre = local + ' vs ' + visitante
        evento = Evento.objects.create(nombre=nombre, equipo_local=local, equipo_visitante=visitante, inicia_en=fecha, estado=EstadoEvento.PROGRAMADO)
        crear_mercados_por_defecto(evento)
        messages.success(request, 'Evento creado: ' + str(evento))
        return redirect('dashboard-eventos')
    eventos = Evento.objects.all().order_by('-inicia_en')
    return render(request, 'dashboard/eventos.html', {'eventos': eventos})

@login_required
@user_passes_test(es_operador)
def evento_detalle(request, evento_id):
    evento = get_object_or_404(Evento, pk=evento_id)
    if request.method == 'POST':
        accion = request.POST.get('accion')
        if accion == 'generar_mercados':
            crear_mercados_por_defecto(evento)
            messages.success(request, 'Mercados generados (1X2, Over/Under y Ambos anotan).')
            return redirect('dashboard-evento-detalle', evento_id=evento.id)
        if accion == 'guardar_cuotas':
            for cuota in Cuota.objects.filter(mercado__evento=evento):
                valor_texto = request.POST.get('valor_' + str(cuota.id), '').strip()
                if valor_texto:
                    try:
                        cuota.valor = Decimal(valor_texto)
                    except InvalidOperation:
                        messages.error(request, 'Hay un valor de cuota invalido.')
                        return redirect('dashboard-evento-detalle', evento_id=evento.id)
                cuota.activa = request.POST.get('activa_' + str(cuota.id)) == 'on'
                cuota.save()
            messages.success(request, 'Cuotas actualizadas.')
            return redirect('dashboard-evento-detalle', evento_id=evento.id)
        if accion in ('simular_critico', 'eliminar', 'estado_programado', 'estado_en_vivo', 'estado_finalizado', 'estado_suspendido', 'estado_anulado'):
            destino = ejecutar_accion_sobre_evento(request, evento, accion)
            if destino == 'lista':
                return redirect('dashboard-eventos')
            evento.refresh_from_db()
            return redirect('dashboard-evento-detalle', evento_id=evento.id)
    mercados = []
    for m in evento.mercados.all().order_by('tipo'):
        mercados.append({'mercado': m, 'cuotas': list(m.cuotas.all())})
    return render(request, 'dashboard/evento_detalle.html', {'evento': evento, 'mercados': mercados})

@login_required
@user_passes_test(es_operador)
def gestion_apuestas(request):
    if request.method == 'POST':
        apuesta_id = request.POST.get('apuesta_id')
        accion = request.POST.get('accion')
        if accion in ('liquidar_ganada', 'liquidar_perdida') and apuesta_id:
            gano = accion == 'liquidar_ganada'
            try:
                liquidar_apuesta(apuesta_id, gano)
                if gano:
                    messages.success(request, 'Apuesta liquidada como GANADA.')
                else:
                    messages.success(request, 'Apuesta liquidada como PERDIDA.')
            except ValidationError as e:
                messages.error(request, str(e))
        return redirect('dashboard-apuestas')

    apuestas = Apuesta.objects.select_related('usuario').order_by('-fecha_creacion')[:100]
    return render(request, 'dashboard/apuestas.html', {'apuestas': apuestas})


@login_required
@user_passes_test(es_operador)
def gestion_limites(request):
    if request.method == 'POST':
        limite_id = request.POST.get('limite_id')
        accion = request.POST.get('accion')
        if accion == 'validar_aumento' and limite_id:
            limite = get_object_or_404(LimiteDeposito, pk=limite_id)
            if not limite.monto_pendiente:
                messages.error(request, 'Este limite no tiene aumento pendiente.')
            else:
                try:
                    if limite.puede_aplicar_aumento_pendiente():
                        limite.aplicar_aumento_pendiente()
                    else:
                        limite.monto = limite.monto_pendiente
                        limite.monto_pendiente = None
                        limite.pendiente_desde = None
                        limite.pendiente_aplicable_desde = None
                        limite.enfriamiento_hasta = None
                        limite.save()
                    messages.success(
                        request,
                        'Aumento validado para ' + limite.usuario.username
                        + ' (' + limite.get_periodo_display() + ').',
                    )
                except ValidationError as e:
                    messages.error(request, str(e))
        return redirect('dashboard-limites')

    pendientes = []
    for lim in LimiteDeposito.objects.filter(
        monto_pendiente__isnull=False
    ).select_related('usuario').order_by('-pendiente_desde'):
        pendientes.append({
            'limite': lim,
            'usado': monto_recargado_en_periodo(lim.usuario, lim.periodo),
            'puede_aplicar': lim.puede_aplicar_aumento_pendiente(),
        })

    return render(request, 'dashboard/limites.html', {'limites_pendientes': pendientes})

@login_required
@user_passes_test(es_operador)
def gestion_acciones(request):
    eventos = Evento.objects.all().order_by('-inicia_en')
    if request.method == 'POST':
        evento_id = request.POST.get('evento_id')
        accion = request.POST.get('accion')
        if not evento_id or not accion:
            messages.error(request, 'Elige un evento y una acción.')
            return redirect('dashboard-acciones')
        evento = get_object_or_404(Evento, pk=evento_id)
        ejecutar_accion_sobre_evento(request, evento, accion)
        return redirect('dashboard-acciones')
    return render(request, 'dashboard/acciones.html', {'eventos': eventos})

@login_required
@user_passes_test(es_operador)
def gestion_alertas(request):
    if request.method == 'POST':
        alerta_id = request.POST.get('alerta_id')
        accion = request.POST.get('accion')
        alerta = get_object_or_404(SuspiciousActivity, pk=alerta_id)
        if accion == 'marcar_revisado':
            alerta.estado = 'revisado'
            alerta.save(update_fields=['estado'])
            messages.success(request, 'Alerta marcada como revisada.')
        elif accion == 'marcar_descartado':
            alerta.estado = 'descartado'
            alerta.save(update_fields=['estado'])
            messages.success(request, 'Alerta descartada.')
        elif accion == 'marcar_pendiente':
            alerta.estado = 'pendiente'
            alerta.save(update_fields=['estado'])
            messages.success(request, 'Alerta marcada como pendiente.')
        else:
            messages.error(request, 'Acción no válida.')
        return redirect('dashboard-alertas')
    alertas = SuspiciousActivity.objects.filter(regla='multiples_cuentas_ip').order_by('-fecha_creacion')
    return render(request, 'dashboard/alertas.html', {'alertas': alertas})

@login_required
@user_passes_test(es_operador)
def reporte_csv(request):
    response = HttpResponse(content_type='text/csv')
    nombre = f"reporte_fairbet_{timezone.now().strftime('%Y%m')}.csv"
    response['Content-Disposition'] = f'attachment; filename="{nombre}"'
    writer = csv.writer(response)
    writer.writerow(['id_apuesta', 'usuario', 'tipo', 'estado', 'stake', 'cuota_total', 'ganancia_potencial', 'ganancia_real', 'fecha'])
    for a in Apuesta.objects.select_related('usuario').order_by('fecha_creacion'):
        writer.writerow([str(a.id), a.usuario.username, a.tipo, a.estado, a.monto_apostado, a.cuota_total, a.ganancia_potencial, a.ganancia_real if a.ganancia_real is not None else '', a.fecha_creacion.strftime('%Y-%m-%d %H:%M')])
    return response
