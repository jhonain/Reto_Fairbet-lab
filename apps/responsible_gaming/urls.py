from django.urls import path
from .views import (
    LimitesDepositoView,
    AutoExclusionView,
    MensajeJuegoResponsableView,
    AlertasSospechosasListView,
    AlertaReviewView,
)

urlpatterns = [
    path("limites/", LimitesDepositoView.as_view(), name="limites-deposito"),
    path("autoexclusion/", AutoExclusionView.as_view(), name="autoexclusion"),
    path("mensaje/", MensajeJuegoResponsableView.as_view(), name="mensaje-jr"),
    path("operador/alertas/", AlertasSospechosasListView.as_view(), name="alertas-lista"),
    path("operador/alertas/<uuid:alerta_id>/", AlertaReviewView.as_view(), name="alertas-review"),
]
