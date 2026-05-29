from django.contrib import admin
from django.utils import timezone
from .models import AutoExclusion, LimiteDeposito


@admin.register(AutoExclusion)
class AutoExclusionAdmin(admin.ModelAdmin):
    list_display = (
        "usuario",
        "tipo",
        "fecha_inicio",
        "fecha_fin",
        "activa",
        "fecha_creacion",
        "esta_vigente",
    )
    list_filter = ("tipo", "activa", "fecha_creacion")
    search_fields = ("usuario__username", "usuario__email")
    ordering = ("-fecha_creacion",)
    readonly_fields = ("fecha_creacion", "esta_vigente")

    @admin.display(boolean=True, description="Vigente")
    def esta_vigente(self, obj):
        if not obj.activa:
            return False
        if obj.fecha_fin is None:
            return True
        return obj.fecha_fin > timezone.now()


@admin.register(LimiteDeposito)
class LimiteDepositoAdmin(admin.ModelAdmin):
    list_display = (
        "usuario",
        "periodo",
        "monto",
        "enfriamiento_hasta",
        "fecha_actualizacion",
        "puede_aumentar_admin",
    )
    list_filter = ("periodo", "fecha_actualizacion")
    search_fields = ("usuario__username", "usuario__email")
    ordering = ("-fecha_actualizacion",)
    readonly_fields = ("fecha_actualizacion", "puede_aumentar_admin")

    @admin.display(boolean=True, description="¿Puede aumentar?")
    def puede_aumentar_admin(self, obj):
        return obj.puede_aumentar()