from datetime import date

from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.users.validators import validar_dni, validar_edad


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
