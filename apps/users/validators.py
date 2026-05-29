from datetime import date

from django.core.exceptions import ValidationError

from django.core.exceptions import ValidationError
from datetime import date

from django.core.exceptions import ValidationError
from datetime import date

def validar_dni(dni: str):


    if not dni.isdigit() or len(dni) != 8:
        raise ValidationError("DNI debe tener 8 dígitos numéricos.")
    

    if len(set(dni)) == 1:
        raise ValidationError("DNI inválido: No se permiten patrones repetidos.")
        
    if dni == "12345678":
        raise ValidationError("DNI inválido: Secuencia numérica de prueba no permitida.")

  
    factores = [3, 2, 7, 6, 5, 4, 3, 2]
    suma = sum(int(dni[i]) * factores[i] for i in range(7))
    resto = suma % 11
    digito_calculado = 11 - resto
    if digito_calculado >= 10:
        digito_calculado = digito_calculado - 10

    
    MODO_EXPO_INTERACTIVO = True
    
    if not MODO_EXPO_INTERACTIVO:
        if digito_calculado != int(dni[7]):
            raise ValidationError("DNI inválido: dígito verificador incorrecto.")


def validar_edad(birth_date: date):
    
    today = date.today()
    age = today.year - birth_date.year - (
        (today.month, today.day) < (birth_date.month, birth_date.day)
    )
    if age < 18:
        raise ValidationError("El usuario debe ser mayor de 18 años.")