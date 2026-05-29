from django.contrib import admin
from .models import Evento, Mercado, Cuota, HistorialCuota

# =====================================================================
# 📊 CONFIGURACIONES INLINE (NIVEL 2 - NAVEGACIÓN JERÁRQUICA)
# =====================================================================

class CuotaInline(admin.TabularInline):
    """Permite ver y editar Cuotas directamente dentro de la vista del Mercado"""
    model = Cuota
    extra = 3  
    max_num = 3 
    fields = ("seleccion", "valor", "activa", "es_ganadora")
    verbose_name = "Cuota del Mercado"
    verbose_name_plural = "Cuotas Asociadas"


class MercadoInline(admin.TabularInline):
    """Permite ver y mapear Mercados directamente dentro de la vista del Evento"""
    model = Mercado
    extra = 1
    show_change_link = True


# =====================================================================
# 👥 CLASES ADMIN PRINCIPALES (FUSIÓN BLINDADA CON EL EQUIPO)
# =====================================================================

@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    # Se combinan los list_display originales con la auditoría in-play del Nivel 2
    list_display = ("id", "nombre", "inicia_en", "estado", "es_momento_critico")
    list_filter = ("estado", "es_momento_critico")
    search_fields = ("nombre", "equipo_local", "equipo_visitante")
    ordering = ("inicia_en",)
    inlines = [MercadoInline]
    
    # 🚀 TU ACCIÓN PERSONALIZADA DE CONTROL IN-PLAY
    actions = ["simular_evento_critico_30s"]

    @admin.action(description="Simular Evento Crítico (Suspender mercados por 30s)")
    def simular_evento_critico_30s(self, request, queryset):
        """Dispara concurrentemente el bloqueo de 30s en cascada usando tu modelo"""
        for evento in queryset:
            evento.suspender_por_evento_critico(segundos=30)
        self.message_user(
            request, 
            "Operación exitosa: Se activó el momento crítico y se suspendieron los mercados temporalmente."
        )


@admin.register(Mercado)
class MercadoAdmin(admin.ModelAdmin):
    # Respeta los campos del equipo e inyecta la columna de control de tiempo de suspensión
    list_display = ("id", "evento", "tipo", "estado", "suspendido_hasta")
    list_filter = ("tipo", "estado")
    search_fields = ("evento__nombre",)
    inlines = [CuotaInline]


@admin.register(Cuota)
class CuotaAdmin(admin.ModelAdmin):
    # Conserva la búsqueda relacional del equipo y suma las flags de liquidación
    list_display = ("id", "mercado", "seleccion", "valor", "activa", "es_ganadora")
    list_filter = ("seleccion", "activa", "es_ganadora")
    search_fields = ("mercado__evento__nombre", "id")


@admin.register(HistorialCuota)
class HistorialCuotasAdmin(admin.ModelAdmin):
    # Asegura la visualización de auditoría inmutable requerida
    list_display = ("id", "cuota", "valor", "registrado_en")
    list_filter = ("registrado_en", "cuota")
    search_fields = ("cuota__id",)
    
    # Restricciones de seguridad biyectivas: el historial no se puede alterar manualmente
    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False
    def has_delete_permission(self, request, obj=None): return False