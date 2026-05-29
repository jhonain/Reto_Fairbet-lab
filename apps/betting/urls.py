from django.urls import path
from .views import ApuestaSimpleView, LiquidarApuestaView, MisApuestasView

urlpatterns = [
    path("mis/", MisApuestasView.as_view(), name="mis-apuestas"),
    path("simple/", ApuestaSimpleView.as_view(), name="apuesta-simple"),
    path("<uuid:apuesta_id>/liquidar/", LiquidarApuestaView.as_view(), name="liquidar-apuesta"),
]
