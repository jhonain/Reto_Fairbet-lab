from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from django.core.exceptions import ValidationError

from apps.wallet.models import asegurar_cuenta_usuario, asegurar_cuentas_sistema
from apps.responsible_gaming.helpers import crear_limites_por_defecto
from .models import PerfilUsuario
from .choices import EstadoKYC


class RegistroView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        dni = request.data.get("dni")
        fecha_nacimiento = request.data.get("fecha_nacimiento")

        if not all([username, password, dni, fecha_nacimiento]):
            return Response(
                {"error": "username, password, dni y fecha_nacimiento son obligatorios."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if User.objects.filter(username=username).exists():
            return Response({"error": "Usuario ya existe."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.create_user(username=username, password=password)
            PerfilUsuario.objects.create(
                usuario=user,
                dni=dni,
                fecha_nacimiento=fecha_nacimiento,
                estado_kyc=EstadoKYC.PENDIENTE,
            )
            asegurar_cuentas_sistema()
            asegurar_cuenta_usuario(user)
            crear_limites_por_defecto(user)
        except ValidationError as e:
            user.delete()
            msg = getattr(e, "message_dict", None) or str(e)
            return Response({"error": msg}, status=status.HTTP_400_BAD_REQUEST)

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
