from django.urls import path
from .views import (
    ApuestaSimpleView,
    LiquidarApuestaView,
    MisApuestasView,
    ApuestaCombinadaView,
    CashOutPreviewView,
    CashOutExecuteView,
)

urlpatterns = [
    path("mis/", MisApuestasView.as_view(), name="mis-apuestas"),
    path("simple/", ApuestaSimpleView.as_view(), name="apuesta-simple"),
    path("combinada/", ApuestaCombinadaView.as_view(), name="apuesta-combinada"),
    path("<uuid:apuesta_id>/liquidar/", LiquidarApuestaView.as_view(), name="liquidar-apuesta"),
    path("<uuid:apuesta_id>/cash-out/", CashOutPreviewView.as_view(), name="cash-out-preview"),
    path("<uuid:apuesta_id>/cash-out/ejecutar/", CashOutExecuteView.as_view(), name="cash-out-ejecutar"),
]
