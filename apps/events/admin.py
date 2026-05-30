from django.contrib import admin
from .models import Evento, Mercado, Cuota, HistorialCuota

@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'inicia_en', 'estado', 'es_momento_critico')
    list_filter = ('estado', 'es_momento_critico')
    search_fields = ('nombre', 'equipo_local', 'equipo_visitante')
    actions = ['simular_evento_critico']

    @admin.action(description='Simular Evento Crítico (Suspender mercados por 30s)')
    def simular_evento_critico(self, request, queryset):
        for evento in queryset:
            evento.suspender_por_evento_critico(segundos=30)
        self.message_user(request, 'Se activó el momento crítico y se suspendieron los mercados por 30 segundos.')

@admin.register(Mercado)
class MercadoAdmin(admin.ModelAdmin):
    list_display = ('id', 'evento', 'tipo', 'estado', 'suspendido_hasta')
    list_filter = ('tipo', 'estado')
    search_fields = ('evento__nombre',)

@admin.register(Cuota)
class CuotaAdmin(admin.ModelAdmin):
    list_display = ('id', 'mercado', 'seleccion', 'valor')
    list_filter = ('seleccion',)
    search_fields = ('mercado__evento__nombre',)

@admin.register(HistorialCuota)
class HistorialCuotasAdmin(admin.ModelAdmin):
    list_display = ('id', 'cuota', 'valor', 'registrado_en')
    list_filter = ('cuota',)
    search_fields = ('cuota__id',)
