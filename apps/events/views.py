from decimal import Decimal

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from django.core.exceptions import ValidationError
from django.utils import timezone
from .serializers import EventoSerializer, MercadoSerializer, CuotaSerializer

from .models import Evento, Mercado, Cuota, HistorialCuota
from .choices import EstadoEvento, TipoMercado, EstadoMercado, MotivoSuspension


class EventosListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        estado = request.query_params.get("estado", EstadoEvento.PROGRAMADO)
        eventos = Evento.objects.filter(estado=estado).order_by("inicia_en")[:50]
        data = []
        for ev in eventos:
            mercado = ev.mercados.filter(tipo=TipoMercado.UNO_X_DOS).first()
            cuotas = []
            if mercado:
                for c in mercado.cuotas.filter(activa=True):
                    cuotas.append({
                        "id": str(c.id),
                        "seleccion": c.seleccion,
                        "valor": str(c.valor),
                    })
            data.append({
                "id": str(ev.id),
                "nombre": ev.nombre,
                "equipo_local": ev.equipo_local,
                "equipo_visitante": ev.equipo_visitante,
                "inicia_en": ev.inicia_en.isoformat(),
                "estado": ev.estado,
                "cuotas_1x2": cuotas,
            })
        return Response(data)


class EventoManageView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        eventos = Evento.objects.all().order_by("-inicia_en")
        data = []
        for ev in eventos:
            data.append({
                "id": str(ev.id),
                "nombre": ev.nombre,
                "equipo_local": ev.equipo_local,
                "equipo_visitante": ev.equipo_visitante,
                "inicia_en": ev.inicia_en.isoformat(),
                "estado": ev.estado,
                "resultado": ev.resultado,
                "es_momento_critico": ev.es_momento_critico,
            })
        return Response(data)

    def post(self, request):
        nombre = request.data.get("nombre")
        equipo_local = request.data.get("equipo_local")
        equipo_visitante = request.data.get("equipo_visitante")
        inicia_en = request.data.get("inicia_en")

        if not all([nombre, equipo_local, equipo_visitante, inicia_en]):
            return Response({"error": "Faltan campos obligatorios."}, status=status.HTTP_400_BAD_REQUEST)

        evento = Evento.objects.create(
            nombre=nombre,
            equipo_local=equipo_local,
            equipo_visitante=equipo_visitante,
            inicia_en=inicia_en,
            deporte=request.data.get("deporte", "futbol"),
        )
        return Response({"id": str(evento.id), "nombre": evento.nombre}, status=status.HTTP_201_CREATED)


class CambiarEstadoEventoView(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, evento_id):
        try:
            evento = Evento.objects.get(pk=evento_id)
        except Evento.DoesNotExist:
            return Response({"error": "Evento no encontrado."}, status=status.HTTP_404_NOT_FOUND)

        nuevo_estado = request.data.get("estado")
        if nuevo_estado not in EstadoEvento.values:
            return Response({"error": f"Estado inválido. Opciones: {EstadoEvento.values}"}, status=status.HTTP_400_BAD_REQUEST)

        evento.estado = nuevo_estado
        evento.ultimo_cambio_estado = timezone.now()
        evento.save(update_fields=["estado", "ultimo_cambio_estado"])

        return Response({
            "id": str(evento.id),
            "estado": evento.estado,
            "mensaje": f"Evento cambiado a {nuevo_estado}",
        })


class MarcarResultadoView(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, evento_id):
        try:
            evento = Evento.objects.get(pk=evento_id)
        except Evento.DoesNotExist:
            return Response({"error": "Evento no encontrado."}, status=status.HTTP_404_NOT_FOUND)

        if evento.estado != EstadoEvento.FINALIZADO:
            return Response({"error": "El evento debe estar finalizado para marcar resultado."}, status=status.HTTP_400_BAD_REQUEST)

        resultado = request.data.get("resultado")
        if not resultado or "local" not in resultado or "visitante" not in resultado:
            return Response({"error": "Resultado debe tener 'local' y 'visitante'."}, status=status.HTTP_400_BAD_REQUEST)

        evento.resultado = resultado
        evento.save(update_fields=["resultado"])

        return Response({
            "id": str(evento.id),
            "resultado": evento.resultado,
            "mensaje": "Resultado registrado. Ahora puedes liquidar las apuestas.",
        })


class SuspenderMercadoView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, mercado_id):
        try:
            mercado = Mercado.objects.get(pk=mercado_id)
        except Mercado.DoesNotExist:
            return Response({"error": "Mercado no encontrado."}, status=status.HTTP_404_NOT_FOUND)

        segundos = request.data.get("segundos")
        try:
            mercado.suspender(
                motivo=MotivoSuspension.MANUAL,
                segundos=int(segundos) if segundos else None,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "id": str(mercado.id),
            "estado": mercado.estado,
            "suspendido_hasta": mercado.suspendido_hasta.isoformat() if mercado.suspendido_hasta else None,
            "mensaje": "Mercado suspendido.",
        })


class ReabrirMercadoView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, mercado_id):
        try:
            mercado = Mercado.objects.get(pk=mercado_id)
        except Mercado.DoesNotExist:
            return Response({"error": "Mercado no encontrado."}, status=status.HTTP_404_NOT_FOUND)

        if mercado.estado != EstadoMercado.SUSPENDIDO:
            return Response({"error": "El mercado no está suspendido."}, status=status.HTTP_400_BAD_REQUEST)

        mercado.reabrir()
        return Response({
            "id": str(mercado.id),
            "estado": mercado.estado,
            "mensaje": "Mercado reabierto.",
        })


class ActualizarCuotaView(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, cuota_id):
        try:
            cuota = Cuota.objects.get(pk=cuota_id)
        except Cuota.DoesNotExist:
            return Response({"error": "Cuota no encontrada."}, status=status.HTTP_404_NOT_FOUND)

        try:
            nuevo_valor = Decimal(str(request.data.get("valor", "0")))
        except Exception:
            return Response({"error": "Valor inválido."}, status=status.HTTP_400_BAD_REQUEST)

        if nuevo_valor <= 0:
            return Response({"error": "El valor debe ser positivo."}, status=status.HTTP_400_BAD_REQUEST)

        HistorialCuota.objects.create(cuota=cuota, valor=cuota.valor)

        cuota.valor = nuevo_valor
        cuota.save(update_fields=["valor"])

        return Response({
            "id": str(cuota.id),
            "seleccion": cuota.seleccion,
            "valor": str(cuota.valor),
            "mensaje": "Cuota actualizada.",
        })

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