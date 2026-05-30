from datetime import timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.events.models import Evento, Mercado, Cuota
from apps.events.choices import EstadoEvento, TipoMercado, CodigoSeleccion

class Command(BaseCommand):
    help = 'Carga eventos de demo para el catálogo.'

    def _crear_mercados(self, evento):
        m_1x2, _ = Mercado.objects.get_or_create(evento=evento, tipo=TipoMercado.UNO_X_DOS, defaults={'margen_operador': Decimal('0.0500')})
        for sel, valor in [(CodigoSeleccion.LOCAL, Decimal('2.1000')), (CodigoSeleccion.EMPATE, Decimal('3.2000')), (CodigoSeleccion.VISITANTE, Decimal('3.5000'))]:
            Cuota.objects.update_or_create(mercado=m_1x2, seleccion=sel, defaults={'valor': valor, 'activa': True})
        m_ou, _ = Mercado.objects.get_or_create(evento=evento, tipo=TipoMercado.SOBRE_BAJO, defaults={'margen_operador': Decimal('0.0500')})
        for sel, valor in [(CodigoSeleccion.SOBRE, Decimal('1.9000')), (CodigoSeleccion.BAJO, Decimal('1.8000'))]:
            Cuota.objects.update_or_create(mercado=m_ou, seleccion=sel, defaults={'valor': valor, 'activa': True})
        m_btts, _ = Mercado.objects.get_or_create(evento=evento, tipo=TipoMercado.AMBOS_ANOTAN, defaults={'margen_operador': Decimal('0.0500')})
        for sel, valor in [(CodigoSeleccion.SI, Decimal('1.7000')), (CodigoSeleccion.NO, Decimal('2.0000'))]:
            Cuota.objects.update_or_create(mercado=m_btts, seleccion=sel, defaults={'valor': valor, 'activa': True})

    def handle(self, *args, **options):
        eventos = [('Perú', 'Chile', 'Perú vs Chile - amistoso', 2), ('Brasil', 'Argentina', 'Brasil vs Argentina - clásico', 3)]
        for local, visitante, nombre, dias in eventos:
            ev, _ = Evento.objects.get_or_create(equipo_local=local, equipo_visitante=visitante, defaults={'nombre': nombre, 'inicia_en': timezone.now() + timedelta(days=dias), 'estado': EstadoEvento.PROGRAMADO})
            self._crear_mercados(ev)
            self.stdout.write(self.style.SUCCESS(f'Evento demo: {ev}'))
