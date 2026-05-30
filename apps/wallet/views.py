import uuid
from decimal import Decimal, InvalidOperation
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.exceptions import ValidationError
from .models import Cuenta, ServicioBilletera, asegurar_cuenta_usuario, asegurar_cuentas_sistema
from .choices import TipoCuenta
from apps.responsible_gaming.services import validar_limite_recarga

def _leer_clave_idempotencia(request):
    raw = request.headers.get('Idempotency-Key') or request.data.get('clave_idempotencia')
    if not raw:
        return None
    try:
        return uuid.UUID(str(raw))
    except ValueError:
        return None

class SaldoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        asegurar_cuenta_usuario(request.user)
        cuenta = Cuenta.objects.get(usuario=request.user, tipo_cuenta=TipoCuenta.BILLETERA_USUARIO)
        return Response({'saldo': str(cuenta.saldo), 'moneda': cuenta.moneda})

class RecargaView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        clave = _leer_clave_idempotencia(request)
        if clave is None:
            return Response({'error': 'Falta Idempotency-Key (UUID).'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            monto = Decimal(str(request.data.get('monto', '0')))
        except (InvalidOperation, TypeError):
            return Response({'error': 'Monto inválido.'}, status=status.HTTP_400_BAD_REQUEST)
        if monto <= 0:
            return Response({'error': 'El monto debe ser positivo.'}, status=status.HTTP_400_BAD_REQUEST)
        asegurar_cuentas_sistema()
        asegurar_cuenta_usuario(request.user)
        try:
            validar_limite_recarga(request.user, monto)
            ServicioBilletera.recargar(request.user, monto, clave)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        cuenta = Cuenta.objects.get(usuario=request.user, tipo_cuenta=TipoCuenta.BILLETERA_USUARIO)
        return Response({'saldo': str(cuenta.saldo), 'moneda': cuenta.moneda})

class RetiroView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        clave = _leer_clave_idempotencia(request)
        if clave is None:
            return Response({'error': 'Falta Idempotency-Key (UUID).'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            monto = Decimal(str(request.data.get('monto', '0')))
        except (InvalidOperation, TypeError):
            return Response({'error': 'Monto inválido.'}, status=status.HTTP_400_BAD_REQUEST)
        asegurar_cuentas_sistema()
        asegurar_cuenta_usuario(request.user)
        try:
            ServicioBilletera.retirar(request.user, monto, clave)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        cuenta = Cuenta.objects.get(usuario=request.user, tipo_cuenta=TipoCuenta.BILLETERA_USUARIO)
        return Response({'saldo': str(cuenta.saldo)})

class TransferenciaView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        clave = _leer_clave_idempotencia(request)
        if clave is None:
            return Response({'error': 'Falta Idempotency-Key.'}, status=status.HTTP_400_BAD_REQUEST)
        destino = request.data.get('usuario_destino')
        if not destino:
            return Response({'error': 'usuario_destino obligatorio.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            monto = Decimal(str(request.data.get('monto', '0')))
        except (InvalidOperation, TypeError):
            return Response({'error': 'Monto inválido.'}, status=status.HTTP_400_BAD_REQUEST)
        asegurar_cuenta_usuario(request.user)
        try:
            ServicioBilletera.transferir(request.user, destino, monto, clave)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        cuenta = Cuenta.objects.get(usuario=request.user, tipo_cuenta=TipoCuenta.BILLETERA_USUARIO)
        return Response({'saldo': str(cuenta.saldo), 'transferido': str(monto)})
