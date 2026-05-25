from django.contrib import admin
from .models import PerfilUsuario


@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = (
        "usuario",
        "dni",
        "estado_kyc",
        "fecha_nacimiento",
        "fecha_verificacion_kyc",
        "fecha_creacion",
        "puede_apostar",
    )
    list_filter = ("estado_kyc", "fecha_creacion", "fecha_verificacion_kyc")
    search_fields = ("usuario__username", "usuario__email", "dni", "telefono")
    ordering = ("-fecha_creacion",)
    readonly_fields = ("fecha_creacion", "fecha_verificacion_kyc", "puede_apostar")