import uuid
from decimal import Decimal
from django.contrib.auth.models import User
from django.test import TestCase
from django.core.exceptions import ValidationError
from apps.wallet.models import ServicioBilletera, asegurar_cuentas_sistema, asegurar_cuenta_usuario
from apps.wallet.tests import _dni_valido
from apps.users.models import PerfilUsuario
from apps.users.choices import EstadoKYC
from apps.responsible_gaming.helpers import crear_limites_por_defecto
from apps.responsible_gaming.models import LimiteDeposito, AutoExclusion
from apps.responsible_gaming.choices import PeriodoLimite, TipoExclusion
from apps.responsible_gaming.services import validar_limite_recarga

class LimitesDepositoTests(TestCase):

    def setUp(self):
        asegurar_cuentas_sistema()
        self.user = User.objects.create_user('lim', password='x')
        PerfilUsuario.objects.create(usuario=self.user, dni=_dni_valido(), fecha_nacimiento='2000-01-01', estado_kyc=EstadoKYC.VERIFICADO)
        crear_limites_por_defecto(self.user)
        asegurar_cuenta_usuario(self.user)

    def test_recarga_respeta_limite_diario(self):
        lim = LimiteDeposito.objects.get(usuario=self.user, periodo=PeriodoLimite.DIARIO)
        lim.monto = Decimal('50.0000')
        lim.save()
        ServicioBilletera.recargar(self.user, Decimal('30.0000'), uuid.uuid4())
        with self.assertRaises(ValidationError):
            validar_limite_recarga(self.user, Decimal('30.0000'))

    def test_subir_limite_requiere_cooldown(self):
        lim = LimiteDeposito.objects.get(usuario=self.user, periodo=PeriodoLimite.DIARIO)
        monto_inicial = lim.monto
        nuevo_monto = Decimal('600.0000')
        lim.actualizar_monto(nuevo_monto)
        lim.refresh_from_db()
        self.assertEqual(lim.monto, monto_inicial)
        self.assertEqual(lim.monto_pendiente, nuevo_monto)
        self.assertIsNotNone(lim.pendiente_aplicable_desde)
        self.assertIsNotNone(lim.enfriamiento_hasta)
        with self.assertRaises(ValidationError):
            lim.aplicar_aumento_pendiente()

class AutoExclusionTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user('exc', password='x')

    def test_temporal_7_tiene_fecha_fin(self):
        ex = AutoExclusion.objects.create(usuario=self.user, tipo=TipoExclusion.TEMPORAL_7)
        self.assertIsNotNone(ex.fecha_fin)
