import uuid
from decimal import Decimal
from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from apps.users.models import PerfilUsuario
from apps.users.choices import EstadoKYC
from apps.wallet.models import asegurar_cuentas_sistema, asegurar_cuenta_usuario, ServicioBilletera, Cuenta
from apps.wallet.choices import TipoCuenta
from apps.events.models import Evento, Mercado, Cuota
from apps.events.choices import EstadoEvento, TipoMercado, CodigoSeleccion
from apps.wallet.tests import _dni_valido
from .services import crear_apuesta_simple, liquidar_apuesta, MONTO_MINIMO
from .choices import EstadoApuesta


class ApuestaSimpleTests(TestCase):
    def setUp(self):
        asegurar_cuentas_sistema()
        self.user = User.objects.create_user("apostador", password="x")
        PerfilUsuario.objects.create(
            usuario=self.user,
            dni=_dni_valido(),
            fecha_nacimiento="2000-01-01",
            estado_kyc=EstadoKYC.VERIFICADO,
        )
        asegurar_cuenta_usuario(self.user)
        ServicioBilletera.recargar(self.user, Decimal("500.0000"), uuid.uuid4())

        inicio = timezone.now() + timedelta(days=1)
        self.evento = Evento.objects.create(
            nombre="Demo",
            equipo_local="A",
            equipo_visitante="B",
            inicia_en=inicio,
            estado=EstadoEvento.PROGRAMADO,
        )
        self.mercado = Mercado.objects.create(evento=self.evento, tipo=TipoMercado.UNO_X_DOS)
        self.cuota = Cuota.objects.create(
            mercado=self.mercado, seleccion=CodigoSeleccion.LOCAL, valor=Decimal("2.5000")
        )

    def test_apuesta_aceptada_y_payout(self):
        apuesta = crear_apuesta_simple(
            self.user,
            self.cuota.id,
            MONTO_MINIMO,
            "clave-test-1",
            True,
        )
        self.assertEqual(apuesta.estado, EstadoApuesta.ACEPTADA)
        self.assertEqual(apuesta.ganancia_potencial, MONTO_MINIMO * Decimal("2.5000"))

        liquidar_apuesta(apuesta.id, gano=True)
        apuesta.refresh_from_db()
        self.assertEqual(apuesta.estado, EstadoApuesta.GANADA)
        self.assertEqual(apuesta.ganancia_real, MONTO_MINIMO * Decimal("2.5000"))

        cuenta = Cuenta.objects.get(usuario=self.user, tipo_cuenta=TipoCuenta.BILLETERA_USUARIO)
        # Tras ganar: tenía 500, bloqueó 1, paga 2.5 -> saldo esperado 500 - 1 + 2.5 = 501.5
        self.assertEqual(cuenta.saldo, Decimal("501.5000"))
