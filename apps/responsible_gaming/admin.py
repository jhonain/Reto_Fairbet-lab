from django.contrib import admin
from django.utils import timezone
from .models import AutoExclusion, SuspiciousActivity, LimiteDeposito

@admin.register(AutoExclusion)
class AutoExclusionAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'tipo', 'fecha_inicio', 'fecha_fin', 'activa', 'fecha_creacion', 'esta_vigente')
    list_filter = ('tipo', 'activa', 'fecha_creacion')
    search_fields = ('usuario__username', 'usuario__email')
    ordering = ('-fecha_creacion',)
    readonly_fields = ('fecha_creacion', 'esta_vigente')

    @admin.display(boolean=True, description='Vigente')
    def esta_vigente(self, obj):
        if not obj.activa:
            return False
        if obj.fecha_fin is None:
            return True
        return obj.fecha_fin > timezone.now()

@admin.register(LimiteDeposito)
class LimiteDepositoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'periodo', 'monto', 'monto_pendiente', 'pendiente_aplicable_desde', 'enfriamiento_hasta', 'fecha_actualizacion', 'puede_aumentar_admin', 'puede_aplicar_pendiente_admin')
    list_filter = ('periodo', 'fecha_actualizacion')
    search_fields = ('usuario__username', 'usuario__email')
    ordering = ('-fecha_actualizacion',)
    readonly_fields = ('fecha_actualizacion', 'puede_aumentar_admin', 'puede_aplicar_pendiente_admin')

    @admin.display(boolean=True, description='Puede aumentar')
    def puede_aumentar_admin(self, obj):
        return obj.puede_aumentar()

    @admin.display(boolean=True, description='Puede aplicar pendiente')
    def puede_aplicar_pendiente_admin(self, obj):
        return obj.puede_aplicar_aumento_pendiente()

@admin.register(SuspiciousActivity)
class SuspiciousActivityAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'regla', 'estado', 'ip_address', 'fecha_creacion')
    list_filter = ('regla', 'estado', 'fecha_creacion')
    search_fields = ('usuario__username', 'ip_address', 'descripcion')
    ordering = ('-fecha_creacion',)
    readonly_fields = ('fecha_creacion',)
