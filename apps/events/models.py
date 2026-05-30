import uuid
from decimal import Decimal
from django.db import models
from django.core.exceptions import ValidationError
from .choices import EstadoEvento, TipoMercado, EstadoMercado, MotivoSuspension, CodigoSeleccion
from django.utils import timezone
from datetime import timedelta
from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import threading
import time

class Evento(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=200, verbose_name='Nombre del evento')
    deporte = models.CharField(max_length=50, default='futbol', verbose_name='Deporte')
    equipo_local = models.CharField(max_length=100, verbose_name='Equipo local')
    equipo_visitante = models.CharField(max_length=100, verbose_name='Equipo visitante')
    inicia_en = models.DateTimeField(verbose_name='Fecha y hora de inicio')
    estado = models.CharField(max_length=15, choices=EstadoEvento.choices, default=EstadoEvento.PROGRAMADO, verbose_name='Estado')
    resultado = models.JSONField(null=True, blank=True, help_text='{"local": 2, "visitante": 1}', verbose_name='Resultado final')
    es_momento_critico = models.BooleanField(default=False, verbose_name='¿Momento crítico?')
    momento_critico_desde = models.DateTimeField(null=True, blank=True, verbose_name='Momento crítico desde')
    ultimo_cambio_estado = models.DateTimeField(auto_now_add=True, verbose_name='Último cambio de estado')
    apuestas_cerradas_en = models.DateTimeField(null=True, blank=True, verbose_name='Apuestas cerradas en')
    desempate_fair_play = models.JSONField(null=True, blank=True, help_text='{"tarjetas_amarillas_local": 2, "tarjetas_rojas_local": 0, ...}', verbose_name='Desempate fair play')

    class Meta:
        db_table = 'eventos_evento'
        verbose_name = 'Evento'
        verbose_name_plural = 'Eventos'
        indexes = [models.Index(fields=['estado', 'inicia_en']), models.Index(fields=['es_momento_critico', 'momento_critico_desde'])]

    def __str__(self):
        return f'{self.equipo_local} vs {self.equipo_visitante} ({self.estado})'

    @property
    def estan_apuestas_abiertas(self):
        if self.estado == EstadoEvento.PROGRAMADO:
            if self.apuestas_cerradas_en:
                return timezone.now() < self.apuestas_cerradas_en
            return True
        if self.estado == EstadoEvento.EN_VIVO:
            return not self.es_momento_critico
        return False

    def suspender_por_evento_critico(self, segundos=30):
        if self.es_momento_critico:
            return
        self.es_momento_critico = True
        self.momento_critico_desde = timezone.now()
        self.save(update_fields=['es_momento_critico', 'momento_critico_desde'])
        for mercado in self.mercados.filter(estado=EstadoMercado.ABIERTO):
            mercado.suspender(MotivoSuspension.EVENTO_CRITICO, segundos)

        def restaurar_mercados_despues_de_tiempo():
            time.sleep(segundos)
            self.refresh_from_db()
            self.es_momento_critico = False
            self.save(update_fields=['es_momento_critico'])
            for m in self.mercados.all():
                m.reabrir()
        hilo = threading.Thread(target=restaurar_mercados_despues_de_tiempo, daemon=True)
        hilo.start()

class Mercado(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    evento = models.ForeignKey(Evento, on_delete=models.PROTECT, related_name='mercados', verbose_name='Evento')
    tipo = models.CharField(max_length=20, choices=TipoMercado.choices, verbose_name='Tipo de mercado')
    estado = models.CharField(max_length=15, choices=EstadoMercado.choices, default=EstadoMercado.ABIERTO, verbose_name='Estado')
    suspendido_hasta = models.DateTimeField(null=True, blank=True, verbose_name='Suspendido hasta')
    motivo_suspension = models.CharField(max_length=20, choices=MotivoSuspension.choices, null=True, blank=True, verbose_name='Motivo de suspensión')
    suspendido_por = models.CharField(max_length=20, choices=[('SISTEMA', 'Sistema'), ('OPERADOR', 'Operador')], null=True, blank=True, verbose_name='Suspendido por')
    margen_operador = models.DecimalField(max_digits=5, decimal_places=4, default=Decimal('0.0500'), help_text='Margen de beneficio del operador, ej. 0.05 = 5%', verbose_name='Margen del operador')

    class Meta:
        db_table = 'eventos_mercado'
        verbose_name = 'Mercado'
        verbose_name_plural = 'Mercados'
        unique_together = [['evento', 'tipo']]

    def __str__(self):
        return f'{self.tipo} - {self.evento}'

    def suspender(self, motivo, segundos=None):
        self.estado = EstadoMercado.SUSPENDIDO
        self.motivo_suspension = motivo
        self.suspendido_por = 'SISTEMA' if motivo == MotivoSuspension.EVENTO_CRITICO else 'OPERADOR'
        if segundos:
            self.suspendido_hasta = timezone.now() + timedelta(seconds=segundos)
        self.save(update_fields=['estado', 'motivo_suspension', 'suspendido_por', 'suspendido_hasta'])

    def reabrir(self):
        from django.utils import timezone
        self.estado = EstadoMercado.ABIERTO
        self.suspendido_hasta = None
        self.motivo_suspension = None
        self.suspendido_por = None
        self.save(update_fields=['estado', 'suspendido_hasta', 'motivo_suspension', 'suspendido_por'])

class Cuota(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    mercado = models.ForeignKey(Mercado, on_delete=models.PROTECT, related_name='cuotas', verbose_name='Mercado')
    seleccion = models.CharField(max_length=15, choices=CodigoSeleccion.choices, verbose_name='Selección')
    valor = models.DecimalField(max_digits=10, decimal_places=4, help_text='Formato decimal europeo, ej. 2.5000', verbose_name='Valor de la cuota')
    activa = models.BooleanField(default=True, verbose_name='¿Activa?')
    es_ganadora = models.BooleanField(null=True, blank=True, default=None, verbose_name='¿Es ganadora?')
    liquidada_en = models.DateTimeField(null=True, blank=True, verbose_name='Liquidada en')
    actualizada_en = models.DateTimeField(auto_now=True, verbose_name='Última actualización')

    class Meta:
        db_table = 'eventos_cuota'
        verbose_name = 'Cuota'
        verbose_name_plural = 'Cuotas'
        unique_together = [['mercado', 'seleccion']]

    def __str__(self):
        return f'{self.seleccion} @ {self.valor}'

    def liquidar(self, es_ganadora):
        from django.utils import timezone
        self.es_ganadora = es_ganadora
        self.liquidada_en = timezone.now()
        self.save(update_fields=['es_ganadora', 'liquidada_en'])

class HistorialCuota(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cuota = models.ForeignKey(Cuota, on_delete=models.PROTECT, related_name='historial', verbose_name='Cuota')
    valor = models.DecimalField(max_digits=10, decimal_places=4, verbose_name='Valor histórico')
    registrado_en = models.DateTimeField(auto_now_add=True, verbose_name='Registrado en')

    class Meta:
        db_table = 'eventos_historialcuota'
        verbose_name = 'Historial de cuota'
        verbose_name_plural = 'Historiales de cuotas'
        ordering = ['-registrado_en']

@receiver(post_save, sender=Cuota)
def notificar_cambio_cuota(sender, instance, **kwargs):
    channel_layer = get_channel_layer()
    if channel_layer:
        payload = {'tipo_mensaje': 'actualizacion_cuota', 'cuota_id': str(instance.id), 'seleccion': instance.seleccion, 'nuevo_valor': str(instance.valor), 'activa': instance.activa}
        async_to_sync(channel_layer.group_send)('broadcast_cuotas', {'type': 'enviar_actualizacion_cuota', 'payload': payload})

@receiver(post_save, sender=Mercado)
def notificar_estado_mercado(sender, instance, **kwargs):
    channel_layer = get_channel_layer()
    if channel_layer:
        payload = {'tipo_mensaje': 'estado_mercado', 'mercado_id': str(instance.id), 'evento_id': str(instance.evento.id), 'estado': instance.estado}
        async_to_sync(channel_layer.group_send)('broadcast_cuotas', {'type': 'enviar_actualizacion_cuota', 'payload': payload})
