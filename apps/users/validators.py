from django.core.exceptions import ValidationError
from datetime import date


def validar_dni(dni: str):
    """Dígito verificador DNI peruano (módulo 11, RENIEC)."""
    if not dni.isdigit() or len(dni) != 8:
        raise ValidationError("DNI debe tener 8 dígitos numéricos.")
    factores = [3, 2, 7, 6, 5, 4, 3, 2]
    suma = sum(int(dni[i]) * factores[i] for i in range(7))
    resto = suma % 11
    digito = 11 - resto
    if digito >= 10:
        digito = digito - 10
    if digito != int(dni[7]):
        raise ValidationError("DNI inválido: dígito verificador incorrecto.")


def validar_edad(birth_date: date):
    """Validar que el usuario tenga al menos 18 años."""
    today = date.today()
    age = today.year - birth_date.year - (
        (today.month, today.day) < (birth_date.month, birth_date.day)
    )
    if age < 18:
        raise ValidationError("El usuario debe ser mayor de 18 años.")