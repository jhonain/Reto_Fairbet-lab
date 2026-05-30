from django.contrib import admin
from .models import Apuesta, PiernaApuesta

@admin.register(Apuesta)
class ApuestaAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'tipo', 'estado', 'monto_apostado', 'cuota_total', 'ganancia_potencial', 'ganancia_real', 'monto_cash_out')
    list_filter = ('tipo', 'estado')
    search_fields = ('usuario__username',)

@admin.register(PiernaApuesta)
class PiernaApuestaAdmin(admin.ModelAdmin):
    list_display = ('id', 'apuesta', 'cuota', 'cuota_al_momento', 'es_ganadora')
    list_filter = ('es_ganadora',)
    search_fields = ('apuesta__id', 'cuota__id')
