from django.contrib import admin
from .models import Cuenta, AsientoContable

@admin.register(Cuenta)
class CuentaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'tipo_cuenta', 'moneda', 'fecha_creacion', 'saldo_actual')
    list_filter = ('tipo_cuenta', 'moneda', 'fecha_creacion')
    search_fields = ('usuario__username', 'usuario__email')
    ordering = ('-fecha_creacion',)
    readonly_fields = ('fecha_creacion', 'saldo_actual')

    @admin.display(description='Saldo')
    def saldo_actual(self, obj):
        return obj.saldo

@admin.register(AsientoContable)
class AsientoContableAdmin(admin.ModelAdmin):
    list_display = ('id', 'cuenta', 'monto', 'direccion', 'tipo_asiento', 'id_transaccion', 'id_referencia', 'fecha_creacion')
    list_filter = ('direccion', 'tipo_asiento', 'fecha_creacion')
    search_fields = ('cuenta__usuario__username', 'cuenta__usuario__email', 'id_transaccion', 'id_referencia')
    ordering = ('-fecha_creacion',)
    readonly_fields = ('id', 'cuenta', 'monto', 'direccion', 'id_transaccion', 'tipo_asiento', 'id_referencia', 'notas', 'fecha_creacion')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
