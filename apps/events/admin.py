from django.contrib import admin
from .models import Evento, Mercado, Cuota, HistorialCuota

# 1. Configuración para ver y editar Cuotas dentro del Mercado
class CuotaInline(admin.TabularInline):
    model = Cuota
    extra = 3  
    max_num = 3 
    fields = ("seleccion", "valor", "activa", "es_ganadora")
    verbose_name = "Cuota del Mercado"
    verbose_name_plural = "Cuotas Asociadas"

# 2. Configuración para ver y editar Mercados dentro del Evento
class MercadoInline(admin.TabularInline):
    model = Mercado
    extra = 1
    show_change_link = True

@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "inicia_en", "estado", "es_momento_critico")
    list_filter = ("estado", "es_momento_critico")
    search_fields = ("nombre", "equipo_local", "equipo_visitante")
    ordering = ("inicia_en",)
    inlines = [MercadoInline]
    
    actions = ["simular_evento_critico_30s"]

    @admin.action(description="Simular Evento Crítico (Suspender mercados por 30s)")
    def simular_evento_critico_30s(self, request, queryset):
        for evento in queryset:
            evento.suspender_por_evento_critico(segundos=30)
        self.message_user(
            request, 
            "Operación exitosa: Se activó el momento crítico y se suspendieron los mercados temporalmente."
        )

@admin.register(Mercado)
class MercadoAdmin(admin.ModelAdmin):
    list_display = ("id", "evento", "tipo", "estado", "suspendido_hasta")
    list_filter = ("tipo", "estado")
    search_fields = ("evento__nombre",)
    inlines = [CuotaInline]

@admin.register(Cuota)
class CuotaAdmin(admin.ModelAdmin):
    list_display = ("id", "mercado", "seleccion", "valor", "activa", "es_ganadora")
    list_filter = ("seleccion", "activa", "es_ganadora")
    search_fields = ("mercado__evento__nombre", "id")

@admin.register(HistorialCuota)
class HistorialCuotasAdmin(admin.ModelAdmin):
    list_display = ("id", "cuota", "valor", "registrado_en")
    list_filter = ("registrado_en",)
    search_fields = ("cuota__id",)
    
    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False
    def has_delete_permission(self, request, obj=None): return False