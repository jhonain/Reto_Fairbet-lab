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




class ValidacionDniTests(TestCase):
   
    def test_dni_00000000_es_rechazado(self):
        with self.assertRaises(ValidationError):
            validar_dni("00000000")
    
    def test_dni_patron_repetido_rechazado(self):
        for d in "123456789":
            with self.assertRaises(ValidationError, msg=f"DNI {d*8} debería ser inválido"):
                validar_dni(d * 8)
    
    def test_dni_secuencia_simple_rechazado(self):
        with self.assertRaises(ValidationError):
            validar_dni("12345678") 
    
    def test_dni_valido_real_aceptado(self):
       
        validar_dni("23456781")

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
        "dni": dni or "73701561",  
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

    def test_registro_api_con_dni_corto_devuelve_400(self):
        response = self.post_json(self.datos_registro(username="dni_corto", dni="1234567"))

        self.assertEqual(response.status_code, 400)

    def test_registro_api_con_dni_largo_devuelve_400(self):
        response = self.post_json(self.datos_registro(username="dni_largo", dni="123456789"))

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
            "dni": dni or "87654321",
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

    def test_registro_web_con_dni_corto_no_crea_usuario(self):
        response = self.client.post(
            self.url,
            data=self.datos_registro(username="dni_corto_web", dni="1234567"),
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Usuario.objects.filter(username="dni_corto_web").exists())

    def test_registro_web_con_dni_largo_no_crea_usuario(self):
        response = self.client.post(
            self.url,
            data=self.datos_registro(username="dni_largo_web", dni="123456789"),
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Usuario.objects.filter(username="dni_largo_web").exists())

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
