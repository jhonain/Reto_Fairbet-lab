from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.events.models import Evento, Mercado, Cuota
from apps.events.choices import EstadoEvento, TipoMercado, CodigoSeleccion


class Command(BaseCommand):
    help = "Carga eventos de demo para el catálogo."

    def handle(self, *args, **options):
        inicio = timezone.now() + timedelta(days=2)
        ev, _ = Evento.objects.get_or_create(
            equipo_local="Perú",
            equipo_visitante="Chile",
            defaults={
                "nombre": "Perú vs Chile - amistoso",
                "inicia_en": inicio,
                "estado": EstadoEvento.PROGRAMADO,
            },
        )
        mercado, _ = Mercado.objects.get_or_create(
            evento=ev, tipo=TipoMercado.UNO_X_DOS,
            defaults={"margen_operador": Decimal("0.0500")},
        )
        datos = [
            (CodigoSeleccion.LOCAL, Decimal("2.1000")),
            (CodigoSeleccion.EMPATE, Decimal("3.2000")),
            (CodigoSeleccion.VISITANTE, Decimal("3.5000")),
        ]
        for sel, valor in datos:
            Cuota.objects.update_or_create(
                mercado=mercado, seleccion=sel,
                defaults={"valor": valor, "activa": True},
            )
        self.stdout.write(self.style.SUCCESS(f"Evento demo: {ev}"))
