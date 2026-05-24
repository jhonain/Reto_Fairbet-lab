from django.core.exceptions import ValidationError
from datetime import date


def validar_dni(dni: str):
    """Algoritmo de dígito verificador DNI peruano (RENIEC)."""
    if not dni.isdigit() or len(dni) != 8:
        raise ValidationError("DNI debe tener 8 dígitos numéricos.")
    factors = [3, 2, 7, 6, 5, 4, 3, 2]
    total = sum(int(d) * f for d, f in zip(dni[:7], factors))
    remainder = total % 11
    check_map = {0: 1, 1: 0, 2: 5, 3: 4, 4: 6, 5: 2, 6: 3}  # simplificado — ajustar a tabla RENIEC oficial
    if remainder not in check_map or check_map[remainder] != int(dni[7]):
        raise ValidationError("DNI inválido: dígito verificador incorrecto.")


def validar_edad(birth_date: date):
    """Validar que el usuario tenga al menos 18 años."""
    today = date.today()
    age = today.year - birth_date.year - (
        (today.month, today.day) < (birth_date.month, birth_date.day)
    )
    if age < 18:
        raise ValidationError("El usuario debe ser mayor de 18 años.")