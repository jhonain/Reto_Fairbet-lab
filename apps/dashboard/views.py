from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db.models import Sum, Count
from django.utils import timezone

from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.betting.models import Apuesta
from apps.betting.choices import EstadoApuesta
from apps.wallet.models import AsientoContable
from apps.wallet.choices import TipoAsiento, DireccionAsiento
from apps.responsible_gaming.models import SuspiciousActivity


Usuario = get_user_model()


class DashboardView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        ahora = timezone.now()
        hoy_inicio = ahora.replace(hour=0, minute=0, second=0, microsecond=0)
        ultimas_24h = ahora - timedelta(hours=24)

        ggr = self._calcular_ggr(hoy_inicio)
        exposure = self._calcular_exposure()
        volumen = self._calcular_volumen(hoy_inicio)
        usuarios_activos = self._calcular_usuarios_activos(ultimas_24h)
        total_usuarios = Usuario.objects.count()
        alertas_pendientes = SuspiciousActivity.objects.filter(estado="pendiente").count()
        apuestas_hoy = Apuesta.objects.filter(fecha_creacion__gte=hoy_inicio).count()

        return Response({
            "ggr": str(ggr),
            "exposure": str(exposure),
            "volumen_apuestas": volumen,
            "apuestas_hoy": apuestas_hoy,
            "usuarios_activos_24h": usuarios_activos,
            "total_usuarios": total_usuarios,
            "alertas_pendientes": alertas_pendientes,
            "fecha_actualizacion": ahora.isoformat(),
        })

    def _calcular_ggr(self, desde):
        ganancias_casa = AsientoContable.objects.filter(
            tipo_asiento=TipoAsiento.PERDIDA_APUESTA,
            direccion=DireccionAsiento.CREDITO,
            fecha_creacion__gte=desde,
        ).aggregate(s=Sum("monto"))["s"] or 0

        perdidas_casa = AsientoContable.objects.filter(
            tipo_asiento=TipoAsiento.GANANCIA_APUESTA,
            direccion=DireccionAsiento.DEBITO,
            fecha_creacion__gte=desde,
        ).aggregate(s=Sum("monto"))["s"] or 0

        return ganancias_casa - perdidas_casa

    def _calcular_exposure(self):
        apuestas_activas = Apuesta.objects.filter(
            estado=EstadoApuesta.ACEPTADA,
        )
        total = apuestas_activas.aggregate(s=Sum("monto_apostado"))["s"] or 0
        return total

    def _calcular_volumen(self, desde):
        apuestas = Apuesta.objects.filter(
            fecha_creacion__gte=desde,
        )
        total = apuestas.aggregate(s=Sum("monto_apostado"))["s"] or 0
        cantidad = apuestas.count()
        return {"cantidad": cantidad, "monto_total": str(total)}

    def _calcular_usuarios_activos(self, desde):
        return Apuesta.objects.filter(
            fecha_creacion__gte=desde,
        ).values("usuario").distinct().count()


class ReporteMensualView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        import csv
        from django.http import HttpResponse

        ahora = timezone.now()
        inicio_mes = ahora.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        apuestas = Apuesta.objects.filter(
            fecha_creacion__gte=inicio_mes,
        ).select_related("usuario").order_by("fecha_creacion")

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = f"attachment; filename=reporte-mensual-{ahora.strftime('%Y-%m')}.csv"

        writer = csv.writer(response)
        writer.writerow([
            "Fecha", "Usuario", "Tipo", "Estado", "Monto Apostado",
            "Cuota", "Ganancia Potencial", "Ganancia Real",
        ])

        for a in apuestas:
            writer.writerow([
                a.fecha_creacion.strftime("%Y-%m-%d %H:%M:%S"),
                a.usuario.username,
                a.tipo,
                a.estado,
                str(a.monto_apostado),
                str(a.cuota_total),
                str(a.ganancia_potencial),
                str(a.ganancia_real) if a.ganancia_real is not None else "",
            ])

        return response
