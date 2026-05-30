from django.contrib import admin
from .models import RegistroAuditoria

@admin.register(RegistroAuditoria)
class RegistroAuditoriaAdmin(admin.ModelAdmin):
    list_display = ('evento', 'hash_actual', 'fecha_creacion')
    search_fields = ('evento', 'hash_actual')
    readonly_fields = ('evento', 'payload', 'hash_anterior', 'hash_actual', 'fecha_creacion')
