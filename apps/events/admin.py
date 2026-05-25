from django.contrib import admin
from .models import Evento, Mercado, Cuota, HistorialCuota


@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "inicia_en", "estado")
    list_filter = ("estado",)
    search_fields = ("nombre",)


@admin.register(Mercado)
class MercadoAdmin(admin.ModelAdmin):
    list_display = ("id", "evento", "tipo", "estado")
    list_filter = ("tipo", "estado")
    search_fields = ("evento__nombre",)


@admin.register(Cuota)
class CuotaAdmin(admin.ModelAdmin):
    list_display = ("id", "mercado", "seleccion", "valor")
    list_filter = ("seleccion",)
    search_fields = ("mercado__evento__nombre",)


@admin.register(HistorialCuota)
class HistorialCuotasAdmin(admin.ModelAdmin):
    list_display = ("id", "cuota", "valor", "registrado_en")
    list_filter = ("cuota",)
    search_fields = ("cuota__id",)