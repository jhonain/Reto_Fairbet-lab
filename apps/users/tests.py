from datetime import date
import json

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import Client, TestCase

from apps.responsible_gaming.models import LimiteDeposito
from apps.users.choices import EstadoKYC
from apps.users.models import PerfilUsuario
from apps.users.validators import validar_dni, validar_edad
from apps.wallet.choices import TipoCuenta
from apps.wallet.models import Cuenta


Usuario = get_user_model()


def generar_dni_valido(base="1234567"):
    factores = [3, 2, 7, 6, 5, 4, 3, 2]
    suma = sum(int(base[i]) * factores[i] for i in range(7))
    digito = 11 - (suma % 11)
    if digito >= 10:
        digito -= 10
    return base + str(digito)


class ValidacionDniTests(TestCase):
    def test_dni_valido_no_lanza_error(self):
        dni = generar_dni_valido()

        try:
            validar_dni(dni)
        except ValidationError:
            self.fail("validar_dni lanzo ValidationError para un DNI valido")

    def test_dni_invalido_por_longitud_o_caracteres(self):
        casos_invalidos = ["1234567", "123456789", "1234567A"]

        for dni in casos_invalidos:
            with self.subTest(dni=dni):
                with self.assertRaises(ValidationError):
                    validar_dni(dni)

    def test_dni_invalido_por_digito_verificador(self):
        dni_valido = generar_dni_valido()
        digito_incorrecto = "0" if dni_valido[-1] != "0" else "1"
        dni_invalido = dni_valido[:7] + digito_incorrecto

        with self.assertRaises(ValidationError):
            validar_dni(dni_invalido)


class ValidacionEdadTests(TestCase):
    def test_mayoria_de_edad_valida(self):
        fecha_nacimiento = date(2000, 1, 1)

        try:
            validar_edad(fecha_nacimiento)
        except ValidationError:
            self.fail("validar_edad lanzo ValidationError para un mayor de edad")

    def test_menor_de_edad_rechazado(self):
        fecha_nacimiento = date.today().replace(year=date.today().year - 17)

        with self.assertRaises(ValidationError):
            validar_edad(fecha_nacimiento)


class RegistroUsuarioApiTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = "/api/usuarios/registro/"

    def datos_registro(self, username="nuevo", dni=None, fecha_nacimiento="2000-01-01"):
        return {
            "username": username,
            "password": "clave-segura-123",
            "dni": dni or generar_dni_valido(),
            "fecha_nacimiento": fecha_nacimiento,
        }

    def post_json(self, data):
        return self.client.post(
            self.url,
            data=json.dumps(data),
            content_type="application/json",
        )

    def test_registro_api_exitoso(self):
        response = self.post_json(self.datos_registro())

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["username"], "nuevo")
        self.assertEqual(response.json()["estado_kyc"], EstadoKYC.PENDIENTE)

        user = Usuario.objects.get(username="nuevo")
        self.assertTrue(PerfilUsuario.objects.filter(usuario=user).exists())
        self.assertTrue(
            Cuenta.objects.filter(
                usuario=user,
                tipo_cuenta=TipoCuenta.BILLETERA_USUARIO,
            ).exists()
        )
        self.assertEqual(LimiteDeposito.objects.filter(usuario=user).count(), 3)

    def test_registro_api_con_dni_invalido_devuelve_400(self):
        response = self.post_json(self.datos_registro(username="dni_mal", dni="1234567A"))

        self.assertEqual(response.status_code, 400)

    def test_registro_api_con_menor_de_edad_devuelve_400(self):
        menor_de_edad = date.today().replace(year=date.today().year - 17).isoformat()

        response = self.post_json(
            self.datos_registro(username="menor", fecha_nacimiento=menor_de_edad)
        )

        self.assertEqual(response.status_code, 400)

    def test_registro_api_con_username_repetido_devuelve_400(self):
        Usuario.objects.create_user(username="repetido", password="x")

        response = self.post_json(self.datos_registro(username="repetido"))

        self.assertEqual(response.status_code, 400)

    def test_registro_fallido_no_deja_usuario_creado_a_medias(self):
        response = self.post_json(self.datos_registro(username="fallido", dni="1234567A"))

        self.assertEqual(response.status_code, 400)
        self.assertFalse(Usuario.objects.filter(username="fallido").exists())
        self.assertFalse(PerfilUsuario.objects.filter(usuario__username="fallido").exists())


class RegistroUsuarioWebTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = "/registro/"

    def datos_registro(self, username="webnuevo", dni=None, fecha_nacimiento="2000-01-01"):
        return {
            "username": username,
            "password": "clave-segura-123",
            "dni": dni or generar_dni_valido("7654321"),
            "fecha_nacimiento": fecha_nacimiento,
        }

    def test_registro_web_con_dni_con_letras_no_crea_usuario(self):
        response = self.client.post(
            self.url,
            data=self.datos_registro(username="dni_letras", dni="RRRRRRRR"),
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Usuario.objects.filter(username="dni_letras").exists())
        self.assertFalse(PerfilUsuario.objects.filter(usuario__username="dni_letras").exists())

    def test_registro_web_con_menor_de_edad_no_crea_usuario(self):
        menor_de_edad = date.today().replace(year=date.today().year - 17).isoformat()

        response = self.client.post(
            self.url,
            data=self.datos_registro(
                username="web_menor",
                fecha_nacimiento=menor_de_edad,
            ),
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Usuario.objects.filter(username="web_menor").exists())
        self.assertFalse(PerfilUsuario.objects.filter(usuario__username="web_menor").exists())

    def test_registro_web_correcto_crea_usuario_y_perfil(self):
        response = self.client.post(
            self.url,
            data=self.datos_registro(),
        )

        self.assertEqual(response.status_code, 302)
        user = Usuario.objects.get(username="webnuevo")
        self.assertTrue(PerfilUsuario.objects.filter(usuario=user).exists())
