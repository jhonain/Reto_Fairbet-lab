from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Evento
from .serializers import EventoSerializer
from .choices import EstadoEvento

class EventoViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet que maneja automáticamente el listado y detalle de los eventos.
    Optimizado mediante serializers jerárquicos.
    """
    queryset = Evento.objects.all().order_by("inicia_en")
    serializer_class = EventoSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        """
        Sobrescribimos el queryset para mantener la lógica original del equipo:
        Filtrar por estado (por defecto 'programado') y limitar a 50 resultados.
        """
        queryset = super().get_queryset()
        estado = self.request.query_params.get("estado", EstadoEvento.PROGRAMADO)
        
        # Optimizamos las consultas SQL con prefetch_related para evitar el problema de N+1 queries
        return queryset.filter(estado=estado).prefetch_related('mercados__cuotas')[:50]

    @action(detail=True, methods=['post'], url_path='suspender')
    def suspender_evento(self, request, pk=None):
        """
        Endpoint personalizado: /api/eventos/{id}/suspender/
        Permite simular eventos críticos por API (Goles, expulsiones para In-play Nivel 2).
        """
        evento = self.get_object()
        evento.suspender_por_evento_critico(segundos=30)
        return Response({"status": "Mercados suspendidos automáticamente por evento crítico."})