import uuid
import unittest
from decimal import Decimal
from concurrent.futures import ThreadPoolExecutor, as_completed
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import connection
from django.test import TransactionTestCase, TestCase
from django.db.models import Sum
from .models import Cuenta, AsientoContable, ServicioBilletera, asegurar_cuentas_sistema, asegurar_cuenta_usuario
from .choices import TipoCuenta, DireccionAsiento

def _dni_valido():
    base = '1234567'
    factores = [3, 2, 7, 6, 5, 4, 3, 2]
    suma = sum((int(base[i]) * factores[i] for i in range(7)))
    digito = 11 - suma % 11
    if digito >= 10:
        digito -= 10
    return base + str(digito)

class ServicioBilleteraTests(TestCase):

    def setUp(self):
        asegurar_cuentas_sistema()
        self.user = User.objects.create_user('tester', password='pass1234')
        asegurar_cuenta_usuario(self.user)

    def test_recarga_aumenta_saldo(self):
        clave = uuid.uuid4()
        ServicioBilletera.recargar(self.user, Decimal('100.0000'), clave)
        cuenta = Cuenta.objects.get(usuario=self.user, tipo_cuenta=TipoCuenta.BILLETERA_USUARIO)
        self.assertEqual(cuenta.saldo, Decimal('100.0000'))

    def test_idempotencia_recarga(self):
        clave = uuid.uuid4()
        ServicioBilletera.recargar(self.user, Decimal('50.0000'), clave)
        ServicioBilletera.recargar(self.user, Decimal('50.0000'), clave)
        cuenta = Cuenta.objects.get(usuario=self.user, tipo_cuenta=TipoCuenta.BILLETERA_USUARIO)
        self.assertEqual(cuenta.saldo, Decimal('50.0000'))

    def test_partida_doble_cuadra_por_transaccion(self):
        clave = uuid.uuid4()
        ServicioBilletera.recargar(self.user, Decimal('25.0000'), clave)
        asientos = AsientoContable.objects.filter(id_transaccion=clave)
        deb = sum((a.monto for a in asientos if a.direccion == DireccionAsiento.DEBITO))
        cred = sum((a.monto for a in asientos if a.direccion == DireccionAsiento.CREDITO))
        self.assertEqual(deb, cred)

    def test_saldo_no_negativo(self):
        clave = uuid.uuid4()
        with self.assertRaises(ValidationError):
            ServicioBilletera.retirar(self.user, Decimal('10.0000'), clave)

    def test_bloqueo_apuesta_descuenta_saldo(self):
        ServicioBilletera.recargar(self.user, Decimal('200.0000'), uuid.uuid4())
        id_ap = uuid.uuid4()
        ServicioBilletera.bloquear_para_apuesta(self.user, Decimal('40.0000'), id_ap, uuid.uuid4())
        cuenta = Cuenta.objects.get(usuario=self.user, tipo_cuenta=TipoCuenta.BILLETERA_USUARIO)
        self.assertEqual(cuenta.saldo, Decimal('160.0000'))

class ConcurrenciaRecargaTests(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        asegurar_cuentas_sistema()
        self.user = User.objects.create_user('conc', password='pass1234')
        asegurar_cuenta_usuario(self.user)
        ServicioBilletera.recargar(self.user, Decimal('100.0000'), uuid.uuid4())

    def _retirar(self, monto, clave):
        connection.close()
        try:
            ServicioBilletera.retirar(self.user, monto, clave)
            return 'ok'
        except ValidationError:
            return 'fail'

    @unittest.skipIf(connection.vendor == 'sqlite', 'Concurrencia real se prueba en PostgreSQL (docker)')
    def test_no_doble_gasto_en_retiros_paralelos(self):
        clave1, clave2 = (uuid.uuid4(), uuid.uuid4())
        with ThreadPoolExecutor(max_workers=2) as pool:
            futs = [pool.submit(self._retirar, Decimal('80.0000'), clave1), pool.submit(self._retirar, Decimal('80.0000'), clave2)]
            resultados = [f.result() for f in as_completed(futs)]
        self.assertEqual(sorted(resultados), ['fail', 'ok'])
        cuenta = Cuenta.objects.get(usuario=self.user, tipo_cuenta=TipoCuenta.BILLETERA_USUARIO)
        self.assertEqual(cuenta.saldo, Decimal('20.0000'))
