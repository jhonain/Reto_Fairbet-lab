from decimal import Decimal, InvalidOperation
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.exceptions import ValidationError
from apps.responsible_gaming.constants import MENSAJE_CONSUMO_RESPONSABLE
from .models import Apuesta
from .services import crear_apuesta_simple, crear_apuesta_combinada, liquidar_apuesta, hacer_cash_out

class MisApuestasView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        apuestas = Apuesta.objects.filter(usuario=request.user).order_by('-fecha_creacion')[:30]
        lista = []
        for a in apuestas:
            lista.append({'id': str(a.id), 'tipo': a.tipo, 'estado': a.estado, 'monto_apostado': str(a.monto_apostado), 'cuota_total': str(a.cuota_total), 'ganancia_potencial': str(a.ganancia_potencial), 'ganancia_real': str(a.ganancia_real) if a.ganancia_real is not None else None})
        return Response(lista)

class ApuestaSimpleView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        clave = request.data.get('clave_idempotencia')
        cuota_id = request.data.get('cuota_id')
        acepto = request.data.get('acepto_juego_responsable', False)
        try:
            monto = Decimal(str(request.data.get('monto', '0')))
        except (InvalidOperation, TypeError):
            return Response({'error': 'Monto inválido.'}, status=status.HTTP_400_BAD_REQUEST)
        if not clave:
            return Response({'error': 'clave_idempotencia obligatoria.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            apuesta = crear_apuesta_simple(request.user, cuota_id, monto, clave, acepto)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'id': str(apuesta.id), 'estado': apuesta.estado, 'monto_apostado': str(apuesta.monto_apostado), 'cuota_total': str(apuesta.cuota_total), 'ganancia_potencial': str(apuesta.ganancia_potencial), 'mensaje_consumo_responsable': MENSAJE_CONSUMO_RESPONSABLE}, status=status.HTTP_201_CREATED)

class ApuestaCombinadaView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        clave = request.data.get('clave_idempotencia')
        cuota_ids = request.data.get('cuota_ids')
        acepto = request.data.get('acepto_juego_responsable', False)
        try:
            monto = Decimal(str(request.data.get('monto', '0')))
        except (InvalidOperation, TypeError):
            return Response({'error': 'Monto inválido.'}, status=status.HTTP_400_BAD_REQUEST)
        if not clave:
            return Response({'error': 'clave_idempotencia obligatoria.'}, status=status.HTTP_400_BAD_REQUEST)
        if not isinstance(cuota_ids, list):
            return Response({'error': 'cuota_ids debe ser una lista de IDs de cuota.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            apuesta = crear_apuesta_combinada(request.user, cuota_ids, monto, clave, acepto)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'id': str(apuesta.id), 'tipo': apuesta.tipo, 'estado': apuesta.estado, 'monto_apostado': str(apuesta.monto_apostado), 'cuota_total': str(apuesta.cuota_total), 'ganancia_potencial': str(apuesta.ganancia_potencial), 'num_selecciones': apuesta.piernas.count(), 'mensaje_consumo_responsable': MENSAJE_CONSUMO_RESPONSABLE}, status=status.HTTP_201_CREATED)

class LiquidarApuestaView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, apuesta_id):
        gano = request.data.get('gano')
        if gano is None:
            return Response({'error': 'Enviar ganó: true/false'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            apuesta = liquidar_apuesta(apuesta_id, bool(gano))
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'id': str(apuesta.id), 'estado': apuesta.estado, 'ganancia_real': str(apuesta.ganancia_real or 0)})

class CashOutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, apuesta_id):
        if not Apuesta.objects.filter(id=apuesta_id, usuario=request.user).exists():
            return Response({'error': 'Apuesta no encontrada.'}, status=status.HTTP_404_NOT_FOUND)
        try:
            apuesta = hacer_cash_out(apuesta_id)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'id': str(apuesta.id), 'estado': apuesta.estado, 'monto_cash_out': str(apuesta.monto_cash_out)})
