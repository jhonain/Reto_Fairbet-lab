from datetime import date

from django.core.exceptions import ValidationError


def validar_dni(dni: str):
    if not dni.isdigit() or len(dni) != 8:
        raise ValidationError("El DNI debe tener 8 dígitos numéricos.")


def validar_edad(birth_date: date):
    today = date.today()
    age = today.year - birth_date.year - (
        (today.month, today.day) < (birth_date.month, birth_date.day)
    )
    if age < 18:
        raise ValidationError("El usuario debe ser mayor de 18 años.")
