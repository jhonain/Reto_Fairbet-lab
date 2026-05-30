from django.urls import path
from .views import ApuestaSimpleView, ApuestaCombinadaView, LiquidarApuestaView, CashOutView, MisApuestasView
urlpatterns = [path('mis/', MisApuestasView.as_view(), name='mis-apuestas'), path('simple/', ApuestaSimpleView.as_view(), name='apuesta-simple'), path('combinada/', ApuestaCombinadaView.as_view(), name='apuesta-combinada'), path('<uuid:apuesta_id>/liquidar/', LiquidarApuestaView.as_view(), name='liquidar-apuesta'), path('<uuid:apuesta_id>/cash-out/', CashOutView.as_view(), name='cash-out')]
