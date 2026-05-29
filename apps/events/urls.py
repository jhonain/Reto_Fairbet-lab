from django.urls import path
from .views import (
    EventosListView,
    EventoManageView,
    CambiarEstadoEventoView,
    MarcarResultadoView,
    SuspenderMercadoView,
    ReabrirMercadoView,
    ActualizarCuotaView,
)

urlpatterns = [
    path("", EventosListView.as_view(), name="eventos-lista"),
    path("operador/", EventoManageView.as_view(), name="eventos-manage"),
    path("operador/<uuid:evento_id>/estado/", CambiarEstadoEventoView.as_view(), name="eventos-cambiar-estado"),
    path("operador/<uuid:evento_id>/resultado/", MarcarResultadoView.as_view(), name="eventos-marcar-resultado"),
    path("operador/mercados/<uuid:mercado_id>/suspender/", SuspenderMercadoView.as_view(), name="mercados-suspender"),
    path("operador/mercados/<uuid:mercado_id>/reabrir/", ReabrirMercadoView.as_view(), name="mercados-reabrir"),
    path("operador/cuotas/<uuid:cuota_id>/", ActualizarCuotaView.as_view(), name="cuotas-actualizar"),
]
