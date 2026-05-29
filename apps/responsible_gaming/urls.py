from django.urls import path
from .views import LimitesDepositoView, AutoExclusionView, MensajeJuegoResponsableView

urlpatterns = [
    path("limites/", LimitesDepositoView.as_view(), name="limites-deposito"),
    path("autoexclusion/", AutoExclusionView.as_view(), name="autoexclusion"),
    path("mensaje/", MensajeJuegoResponsableView.as_view(), name="mensaje-jr"),
]
