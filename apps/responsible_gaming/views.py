from decimal import Decimal, InvalidOperation
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.responsible_gaming.services import monto_recargado_en_periodo, obtener_autoexclusion_vigente
from .models import AutoExclusion, LimiteDeposito
from .choices import TipoExclusion, PeriodoLimite

class LimitesDepositoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        limites = LimiteDeposito.objects.filter(usuario=request.user)
        data = []
        for lim in limites:
            usado = monto_recargado_en_periodo(request.user, lim.periodo)
            data.append({'periodo': lim.periodo, 'monto_limite': str(lim.monto), 'monto_usado': str(usado), 'monto_pendiente': str(lim.monto_pendiente) if lim.monto_pendiente else None, 'pendiente_aplicable_desde': lim.pendiente_aplicable_desde.isoformat() if lim.pendiente_aplicable_desde else None, 'puede_aplicar_pendiente': lim.puede_aplicar_aumento_pendiente(), 'enfriamiento_hasta': lim.enfriamiento_hasta.isoformat() if lim.enfriamiento_hasta else None})
        return Response(data)

    def patch(self, request):
        periodo = request.data.get('periodo')
        if periodo not in PeriodoLimite.values:
            return Response({'error': 'periodo invalido (diario/semanal/mensual).'}, status=400)
        limite = LimiteDeposito.objects.filter(usuario=request.user, periodo=periodo).first()
        if request.data.get('accion') == 'aplicar_pendiente':
            if not limite:
                return Response({'error': 'No existe limite para ese periodo.'}, status=400)
            try:
                limite.aplicar_aumento_pendiente()
            except ValidationError as e:
                return Response({'error': str(e)}, status=400)
            return Response({'periodo': limite.periodo, 'monto_limite': str(limite.monto), 'monto_pendiente': None, 'pendiente_aplicable_desde': None, 'mensaje': 'Aumento pendiente aplicado.'})
        try:
            nuevo = Decimal(str(request.data.get('monto')))
        except (InvalidOperation, TypeError):
            return Response({'error': 'monto invalido.'}, status=400)
        if nuevo <= 0:
            return Response({'error': 'El monto debe ser positivo.'}, status=400)
        limite, _ = LimiteDeposito.objects.get_or_create(usuario=request.user, periodo=periodo, defaults={'monto': nuevo})
        monto_anterior = limite.monto
        try:
            limite.actualizar_monto(nuevo)
        except ValidationError as e:
            return Response({'error': str(e)}, status=400)
        mensaje = 'Limite actualizado.'
        if nuevo > monto_anterior:
            mensaje = 'Aumento registrado como pendiente por 24 horas.'
        return Response({'periodo': limite.periodo, 'monto_limite': str(limite.monto), 'monto_pendiente': str(limite.monto_pendiente) if limite.monto_pendiente else None, 'pendiente_aplicable_desde': limite.pendiente_aplicable_desde.isoformat() if limite.pendiente_aplicable_desde else None, 'enfriamiento_hasta': limite.enfriamiento_hasta.isoformat() if limite.enfriamiento_hasta else None, 'mensaje': mensaje})

class AutoExclusionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        exclusion = obtener_autoexclusion_vigente(request.user)
        if not exclusion:
            return Response({'activa': False})
        return Response({'activa': True, 'tipo': exclusion.tipo, 'fecha_inicio': exclusion.fecha_inicio.isoformat(), 'fecha_fin': exclusion.fecha_fin.isoformat() if exclusion.fecha_fin else None})

    def post(self, request):
        tipo = request.data.get('tipo')
        if tipo not in TipoExclusion.values:
            return Response({'error': 'tipo: temporal_7, temporal_30, temporal_90 o indefinida'}, status=400)
        if obtener_autoexclusion_vigente(request.user):
            return Response({'error': 'Ya tienes una autoexclusion activa. No puedes revertirla.'}, status=400)
        exclusion = AutoExclusion.objects.create(usuario=request.user, tipo=tipo)
        return Response({'id': str(exclusion.id), 'tipo': exclusion.tipo, 'fecha_fin': exclusion.fecha_fin.isoformat() if exclusion.fecha_fin else None, 'mensaje': 'Autoexclusion activada. No podras apostar hasta que termine.'}, status=status.HTTP_201_CREATED)

class MensajeJuegoResponsableView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from apps.responsible_gaming.constants import MENSAJE_CONSUMO_RESPONSABLE
        return Response({'mensaje': MENSAJE_CONSUMO_RESPONSABLE})
