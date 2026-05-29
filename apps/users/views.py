from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.wallet.models import asegurar_cuenta_usuario, asegurar_cuentas_sistema
from apps.responsible_gaming.helpers import crear_limites_por_defecto
from apps.responsible_gaming.services import registrar_alerta_multiples_cuentas_ip
from .models import PerfilUsuario
from .choices import EstadoKYC
from .serializers import RegistroUsuarioSerializer


Usuario = get_user_model()


def _obtener_ip_request(request):
    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


class RegistroView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistroUsuarioSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        datos = serializer.validated_data

        with transaction.atomic():
            user = Usuario.objects.create_user(
                username=datos["username"],
                password=datos["password"],
            )
            PerfilUsuario.objects.create(
                usuario=user,
                dni=datos["dni"],
                fecha_nacimiento=datos["fecha_nacimiento"],
                estado_kyc=EstadoKYC.PENDIENTE,
            )
            asegurar_cuentas_sistema()
            asegurar_cuenta_usuario(user)
            crear_limites_por_defecto(user)

        try:
            registrar_alerta_multiples_cuentas_ip(
                user,
                _obtener_ip_request(request),
            )
        except Exception:
            pass

        return Response(
            {"id": user.id, "username": user.username, "estado_kyc": EstadoKYC.PENDIENTE},
            status=status.HTTP_201_CREATED,
        )


class VerificarKYCView(APIView):
    """Simula la verificación manual del operador."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        perfil = request.user.perfil
        perfil.verificar()
        return Response({"estado_kyc": perfil.estado_kyc})


class PerfilView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        perfil = request.user.perfil
        return Response({
            "dni": perfil.dni,
            "estado_kyc": perfil.estado_kyc,
            "puede_apostar": perfil.puede_apostar,
        })
