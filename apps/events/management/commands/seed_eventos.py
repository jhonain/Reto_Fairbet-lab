from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.events.models import Evento, Mercado, Cuota
from apps.events.choices import EstadoEvento, TipoMercado, CodigoSeleccion


class Command(BaseCommand):
    help = "Carga eventos de demo para el catálogo incluyendo mercados del Nivel 2."

    def handle(self, *args, **options):
        inicio = timezone.now() + timedelta(days=2)
        
        # 1. Creamos o recuperamos el Evento base
        ev, _ = Evento.objects.get_or_create(
            equipo_local="Perú",
            equipo_visitante="Chile",
            defaults={
                "nombre": "Perú vs Chile - amistoso",
                "inicia_en": inicio,
                "estado": EstadoEvento.PROGRAMADO,
            },
        )

        # =====================================================================
        # MERCADO 1: 1X2 (Ya lo tenías, mantenemos tu lógica exacta)
        # =====================================================================
        m1x2, _ = Mercado.objects.get_or_create(
            evento=ev, 
            tipo=TipoMercado.UNO_X_DOS,
            defaults={"margen_operador": Decimal("0.0500")},
        )
        datos_1x2 = [
            (CodigoSeleccion.LOCAL, Decimal("2.1000")),
            (CodigoSeleccion.EMPATE, Decimal("3.2000")),
            (CodigoSeleccion.VISITANTE, Decimal("3.5000")),
        ]
        for sel, valor in datos_1x2:
            Cuota.objects.update_or_create(
                mercado=m1x2, seleccion=sel,
                defaults={"valor": valor, "activa": True},
            )

        # =====================================================================
        # MERCADO 2: Over/Under 2.5 Goles (Nivel 2)
        # =====================================================================
        m_ou, _ = Mercado.objects.get_or_create(
            evento=ev, 
            tipo=getattr(TipoMercado, 'OVER_UNDER_25', 'OVER_UNDER_25'),
            defaults={"margen_operador": Decimal("0.0500")},
        )
        datos_ou = [
            (getattr(CodigoSeleccion, 'OVER_25', 'OVER25'), Decimal("1.8500")),  # 💡 Reducido a 'OVER25' (6 chars)
            (getattr(CodigoSeleccion, 'UNDER_25', 'UNDER25'), Decimal("1.9500")), # 💡 Reducido a 'UNDER25' (7 chars)
        ]
        for sel, valor in datos_ou:
            Cuota.objects.update_or_create(
                mercado=m_ou, seleccion=sel,
                defaults={"valor": valor, "activa": True},
            )

        # =====================================================================
        # MERCADO 3: Ambos equipos anotan - BTTS (Nivel 2)
        # =====================================================================
        m_btts, _ = Mercado.objects.get_or_create(
            evento=ev, 
            tipo=getattr(TipoMercado, 'BTTS', 'BTTS'),
            defaults={"margen_operador": Decimal("0.0500")},
        )
        datos_btts = [
            (getattr(CodigoSeleccion, 'BTTS_SI', 'BTTS_SI'), Decimal("1.7000")),   # 💡 'BTTS_SI' (7 chars)
            (getattr(CodigoSeleccion, 'BTTS_NO', 'BTTS_NO'), Decimal("2.0500")),   # 💡 'BTTS_NO' (7 chars)
        ]
        for sel, valor in datos_btts:
            Cuota.objects.update_or_create(
                mercado=m_btts, seleccion=sel,
                defaults={"valor": valor, "activa": True},
            )

        # =====================================================================
        # MERCADO 4: Hándicap Asiático (Nivel 2)
        # =====================================================================
        m_ha, _ = Mercado.objects.get_or_create(
            evento=ev, 
            tipo=getattr(TipoMercado, 'HANDICAP_ASIATICO', 'HANDICAP_ASIATICO'),
            defaults={"margen_operador": Decimal("0.0500")},
        )
        datos_ha = [
            (getattr(CodigoSeleccion, 'HA_LOCAL_MINUS_05', 'HA_L_05'), Decimal("1.9000")), # 💡 Reducido a 'HA_L_05' (7 chars)
            (getattr(CodigoSeleccion, 'HA_VISITANTE_PLUS_05', 'HA_V_05'), Decimal("1.9000")), # 💡 Reducido a 'HA_V_05' (7 chars)
        ]
        for sel, valor in datos_ha:
            Cuota.objects.update_or_create(
                mercado=m_ha, seleccion=sel,
                defaults={"valor": valor, "activa": True},
            )