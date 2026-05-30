import uuid
from decimal import Decimal
from datetime import timedelta

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from apps.users.models import PerfilUsuario
from apps.users.choices import EstadoKYC
from apps.wallet.models import asegurar_cuentas_sistema, asegurar_cuenta_usuario, ServicioBilletera, Cuenta
from apps.wallet.choices import TipoCuenta
from apps.events.models import Evento, Mercado, Cuota
from apps.events.choices import EstadoEvento, TipoMercado, CodigoSeleccion
from apps.wallet.tests import _dni_valido
from .services import (
    crear_apuesta_simple,
    crear_apuesta_combinada,
    liquidar_apuesta,
    calcular_cash_out,
    ejecutar_cash_out,
    MONTO_MINIMO,
)
from .choices import EstadoApuesta, TipoApuesta


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


class RecotizacionTests(TestCase):
    def setUp(self):
        asegurar_cuentas_sistema()
        self.user = User.objects.create_user("recotizador", password="x")
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
            nombre="Re-cotización Test",
            equipo_local="X",
            equipo_visitante="Y",
            inicia_en=inicio,
            estado=EstadoEvento.PROGRAMADO,
        )
        self.mercado = Mercado.objects.create(evento=self.evento, tipo=TipoMercado.UNO_X_DOS)
        self.cuota = Cuota.objects.create(
            mercado=self.mercado, seleccion=CodigoSeleccion.LOCAL, valor=Decimal("3.0000")
        )

    def test_sin_cuota_aceptada_usa_valor_actual(self):
        apuesta = crear_apuesta_simple(
            self.user, self.cuota.id, MONTO_MINIMO, "clave-rec-1", True,
        )
        self.assertEqual(apuesta.cuota_total, Decimal("3.0000"))

    def test_cuota_actual_mayor_usa_actual(self):
        apuesta = crear_apuesta_simple(
            self.user, self.cuota.id, MONTO_MINIMO, "clave-rec-2", True,
            cuota_aceptada=Decimal("2.5000"),
        )
        self.assertEqual(apuesta.cuota_total, Decimal("3.0000"))

    def test_cuota_actual_menor_mantiene_aceptada(self):
        apuesta = crear_apuesta_simple(
            self.user, self.cuota.id, MONTO_MINIMO, "clave-rec-3", True,
            cuota_aceptada=Decimal("4.0000"),
        )
        self.assertEqual(apuesta.cuota_total, Decimal("4.0000"))


class ApuestaCombinadaTests(TestCase):
    def setUp(self):
        asegurar_cuentas_sistema()
        self.user = User.objects.create_user("combinador", password="x")
        PerfilUsuario.objects.create(
            usuario=self.user,
            dni=_dni_valido(),
            fecha_nacimiento="2000-01-01",
            estado_kyc=EstadoKYC.VERIFICADO,
        )
        asegurar_cuenta_usuario(self.user)
        ServicioBilletera.recargar(self.user, Decimal("500.0000"), uuid.uuid4())

        inicio = timezone.now() + timedelta(days=1)
        self.e1 = Evento.objects.create(
            nombre="Evento 1", equipo_local="A", equipo_visitante="B",
            inicia_en=inicio, estado=EstadoEvento.PROGRAMADO,
        )
        self.e2 = Evento.objects.create(
            nombre="Evento 2", equipo_local="C", equipo_visitante="D",
            inicia_en=inicio, estado=EstadoEvento.PROGRAMADO,
        )
        m1 = Mercado.objects.create(evento=self.e1, tipo=TipoMercado.UNO_X_DOS)
        m2 = Mercado.objects.create(evento=self.e2, tipo=TipoMercado.UNO_X_DOS)
        self.c1 = Cuota.objects.create(mercado=m1, seleccion=CodigoSeleccion.LOCAL, valor=Decimal("2.0000"))
        self.c2 = Cuota.objects.create(mercado=m2, seleccion=CodigoSeleccion.LOCAL, valor=Decimal("3.0000"))

    def test_combinada_valida(self):
        apuesta = crear_apuesta_combinada(
            self.user,
            [{"cuota_id": self.c1.id}, {"cuota_id": self.c2.id}],
            MONTO_MINIMO, "clave-comb-1", True,
        )
        self.assertEqual(apuesta.tipo, TipoApuesta.COMBINADA)
        self.assertEqual(apuesta.cuota_total, Decimal("6.0000"))
        self.assertEqual(apuesta.piernas.count(), 2)
        self.assertEqual(apuesta.estado, EstadoApuesta.ACEPTADA)

    def test_combinada_requiere_dos_selecciones(self):
        with self.assertRaisesMessage(ValidationError, "al menos 2 selecciones"):
            crear_apuesta_combinada(
                self.user,
                [{"cuota_id": self.c1.id}],
                MONTO_MINIMO, "clave-comb-2", True,
            )

    def test_combinada_rechaza_mismo_mercado(self):
        c3 = Cuota.objects.create(
            mercado=self.c1.mercado, seleccion=CodigoSeleccion.VISITANTE, valor=Decimal("4.0000"),
        )
        with self.assertRaisesMessage(ValidationError, "Ya elegiste una cuota"):
            crear_apuesta_combinada(
                self.user,
                [{"cuota_id": self.c1.id}, {"cuota_id": c3.id}],
                MONTO_MINIMO, "clave-comb-3", True,
            )

    def test_combinada_mismo_evento_distinto_mercado(self):
        m3 = Mercado.objects.create(evento=self.e1, tipo=TipoMercado.SOBRE_BAJO)
        c3 = Cuota.objects.create(mercado=m3, seleccion=CodigoSeleccion.SOBRE, valor=Decimal("1.8000"))
        apuesta = crear_apuesta_combinada(
            self.user,
            [{"cuota_id": self.c1.id}, {"cuota_id": c3.id}],
            MONTO_MINIMO, "clave-comb-mismo-evento", True,
        )
        self.assertEqual(apuesta.tipo, TipoApuesta.COMBINADA)
        self.assertEqual(apuesta.piernas.count(), 2)
        self.assertEqual(apuesta.cuota_total, Decimal("3.6000"))

    def test_combinada_con_recotizacion(self):
        apuesta = crear_apuesta_combinada(
            self.user,
            [
                {"cuota_id": self.c1.id, "cuota_aceptada": "1.5000"},
                {"cuota_id": self.c2.id, "cuota_aceptada": "4.0000"},
            ],
            MONTO_MINIMO, "clave-comb-4", True,
        )
        # c1 actual=2.0 >= 1.5 -> usa 2.0; c2 actual=3.0 < 4.0 -> mantiene 4.0
        self.assertEqual(apuesta.cuota_total, Decimal("8.0000"))


class CashOutTests(TestCase):
    def setUp(self):
        asegurar_cuentas_sistema()
        self.user = User.objects.create_user("cashouter", password="x")
        PerfilUsuario.objects.create(
            usuario=self.user,
            dni=_dni_valido(),
            fecha_nacimiento="1995-01-01",
            estado_kyc=EstadoKYC.VERIFICADO,
        )
        asegurar_cuenta_usuario(self.user)
        ServicioBilletera.recargar(self.user, Decimal("1000.0000"), uuid.uuid4())

        inicio = timezone.now() + timedelta(days=1)
        self.evento = Evento.objects.create(
            nombre="CashOut Event", equipo_local="A", equipo_visitante="B",
            inicia_en=inicio, estado=EstadoEvento.PROGRAMADO,
        )
        self.mercado = Mercado.objects.create(evento=self.evento, tipo=TipoMercado.UNO_X_DOS)
        self.cuota = Cuota.objects.create(
            mercado=self.mercado, seleccion=CodigoSeleccion.LOCAL, valor=Decimal("4.0000")
        )

    def _crear_apuesta(self, clave):
        return crear_apuesta_simple(self.user, self.cuota.id, Decimal("100.0000"), clave, True)

    def test_calcular_cash_out_preview(self):
        apuesta = self._crear_apuesta("co-clave-1")
        calculo = calcular_cash_out(apuesta.id)
        self.assertEqual(calculo["stake"], Decimal("100.0000"))
        self.assertEqual(calculo["cuota_total_original"], Decimal("4.0000"))
        self.assertEqual(calculo["cuota_total_actual"], Decimal("4.0000"))
        # cash_out = 100 * 4 / 4 * (1-0.03) = 97
        self.assertEqual(calculo["cash_out_final"], Decimal("97.0000"))

    def test_ejecutar_cash_out(self):
        apuesta = self._crear_apuesta("co-clave-2")
        result = ejecutar_cash_out(apuesta.id)
        result.refresh_from_db()
        self.assertEqual(result.estado, EstadoApuesta.CASH_OUT)
        self.assertEqual(result.monto_cash_out, Decimal("97.0000"))

    def test_cash_out_devuelve_saldo_al_usuario(self):
        apuesta = self._crear_apuesta("co-clave-3")
        cuenta = Cuenta.objects.get(usuario=self.user, tipo_cuenta=TipoCuenta.BILLETERA_USUARIO)
        saldo_antes = cuenta.saldo
        ejecutar_cash_out(apuesta.id)
        cuenta.refresh_from_db()
        # Tenía 900 libres (1000-100 bloqueados); cash-out devuelve 97 -> 900+97 = 997
        self.assertEqual(cuenta.saldo, Decimal("997.0000"))

    def test_cash_out_ya_ejecutado_rechaza(self):
        apuesta = self._crear_apuesta("co-clave-4")
        ejecutar_cash_out(apuesta.id)
        with self.assertRaisesMessage(ValidationError, "cash-out de apuestas aceptadas"):
            ejecutar_cash_out(apuesta.id)
