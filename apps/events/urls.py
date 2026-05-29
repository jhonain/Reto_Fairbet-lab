from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from .views import (
    EventosListView,
    EventoManageView,
    CambiarEstadoEventoView,
    MarcarResultadoView,
    SuspenderMercadoView,
    ReabrirMercadoView,
    ActualizarCuotaView,
    EventoViewSet,  # <-- Importamos tu ViewSet del Nivel 2
)

# 🚀 Configuración de tu Router para el catálogo avanzado
router = DefaultRouter()
# Le damos un prefijo vacío aquí porque lo empaquetaremos abajo
router.register(r'', EventoViewSet, basename='evento-v2')

urlpatterns = [
    # 👥 1. Rutas Originales del Equipo (Intactas)
    path("", EventosListView.as_view(), name="eventos-lista"),
    path("operador/", EventoManageView.as_view(), name="eventos-manage"),
    path("operador/<uuid:evento_id>/estado/", CambiarEstadoEventoView.as_view(), name="eventos-cambiar-estado"),
    path("operador/<uuid:evento_id>/resultado/", MarcarResultadoView.as_view(), name="eventos-marcar-resultado"),
    path("operador/mercados/<uuid:mercado_id>/suspender/", SuspenderMercadoView.as_view(), name="mercados-suspender"),
    path("operador/mercados/<uuid:mercado_id>/reabrir/", ReabrirMercadoView.as_view(), name="mercados-reabrir"),
    path("operador/cuotas/<uuid:cuota_id>/", ActualizarCuotaView.as_view(), name="cuotas-actualizar"),

    # ⚡ 2. Tu Endpoint del Nivel 2 (Mapeado bajo el prefijo 'v2/')
    # Esto expone: /api/events/v2/  y  /api/events/v2/{id}/suspender/
    path("v2/", include(router.urls)),
]

# Servidor de archivos estáticos en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)