from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from apps.users.validators import validar_dni, validar_edad


Usuario = get_user_model()


class RegistroUsuarioSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)
    dni = serializers.CharField(required=True)
    fecha_nacimiento = serializers.DateField(required=True)

    def validate_username(self, value):
        if Usuario.objects.filter(username=value).exists():
            raise serializers.ValidationError("Usuario ya existe.")
        return value

    def validate_dni(self, value):
        try:
            validar_dni(value)
        except DjangoValidationError as error:
            raise serializers.ValidationError(error.messages)
        return value

    def validate_fecha_nacimiento(self, value):
        try:
            validar_edad(value)
        except DjangoValidationError as error:
            raise serializers.ValidationError(error.messages)
        return value
