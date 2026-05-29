from decimal import Decimal, InvalidOperation

from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.responsible_gaming.services import monto_recargado_en_periodo
from .models import AutoExclusion, LimiteDeposito
from .choices import TipoExclusion, PeriodoLimite


class LimitesDepositoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        limites = LimiteDeposito.objects.filter(usuario=request.user)
        data = []
        for lim in limites:
            usado = monto_recargado_en_periodo(request.user, lim.periodo)
            data.append({
                "periodo": lim.periodo,
                "monto_limite": str(lim.monto),
                "monto_usado": str(usado),
                "enfriamiento_hasta": (
                    lim.enfriamiento_hasta.isoformat() if lim.enfriamiento_hasta else None
                ),
            })
        return Response(data)

    def patch(self, request):
        periodo = request.data.get("periodo")
        if periodo not in PeriodoLimite.values:
            return Response({"error": "periodo inválido (diario/semanal/mensual)."}, status=400)

        try:
            nuevo = Decimal(str(request.data.get("monto")))
        except (InvalidOperation, TypeError):
            return Response({"error": "monto inválido."}, status=400)

        if nuevo <= 0:
            return Response({"error": "El monto debe ser positivo."}, status=400)

        limite, _ = LimiteDeposito.objects.get_or_create(
            usuario=request.user,
            periodo=periodo,
            defaults={"monto": nuevo},
        )
        try:
            limite.actualizar_monto(nuevo)
        except ValidationError as e:
            return Response({"error": str(e)}, status=400)

        return Response({
            "periodo": limite.periodo,
            "monto_limite": str(limite.monto),
            "enfriamiento_hasta": (
                limite.enfriamiento_hasta.isoformat() if limite.enfriamiento_hasta else None
            ),
        })


class AutoExclusionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        activa = request.user.exclusiones.filter(activa=True).first()
        if not activa:
            return Response({"activa": False})
        return Response({
            "activa": True,
            "tipo": activa.tipo,
            "fecha_inicio": activa.fecha_inicio.isoformat(),
            "fecha_fin": activa.fecha_fin.isoformat() if activa.fecha_fin else None,
        })

    def post(self, request):
        tipo = request.data.get("tipo")
        if tipo not in TipoExclusion.values:
            return Response(
                {"error": "tipo: temporal_7, temporal_30, temporal_90 o indefinida"},
                status=400,
            )

        ya_tiene = request.user.exclusiones.filter(activa=True).filter(
            Q(fecha_fin__isnull=True) | Q(fecha_fin__gt=timezone.now())
        ).exists()
        if ya_tiene:
            return Response(
                {"error": "Ya tienes una autoexclusión activa. No puedes revertirla."},
                status=400,
            )

        exclusion = AutoExclusion.objects.create(usuario=request.user, tipo=tipo)
        return Response({
            "id": str(exclusion.id),
            "tipo": exclusion.tipo,
            "fecha_fin": exclusion.fecha_fin.isoformat() if exclusion.fecha_fin else None,
            "mensaje": "Autoexclusión activada. No podrás apostar hasta que termine.",
        }, status=status.HTTP_201_CREATED)


class MensajeJuegoResponsableView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from apps.responsible_gaming.constants import MENSAJE_CONSUMO_RESPONSABLE
        return Response({"mensaje": MENSAJE_CONSUMO_RESPONSABLE})
