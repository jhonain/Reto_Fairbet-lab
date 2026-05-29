from django.urls import path
from . import views

urlpatterns = [
    path("", views.inicio, name="portal-inicio"),
    path("registro/", views.registro, name="portal-registro"),
    path("cuenta/login/", views.cuenta_login, name="portal-login"),
    path("cuenta/logout/", views.cuenta_logout, name="portal-logout"),
    path("perfil/", views.perfil, name="portal-perfil"),
    path("wallet/", views.wallet, name="portal-wallet"),
    path("eventos/", views.eventos, name="portal-eventos"),
    path("apuestas/", views.apuestas, name="portal-apuestas"),
    path("juego-responsable/", views.juego_responsable, name="portal-responsable"),
    # Operador
    path("operador/", views.operador_dashboard, name="operador-dashboard"),
    path("operador/eventos/", views.operador_eventos, name="operador-eventos"),
    path("operador/apuestas/", views.operador_apuestas, name="operador-apuestas"),
    path("operador/alertas/", views.operador_alertas, name="operador-alertas"),
    path("operador/reporte/", views.operador_reporte, name="operador-reporte"),
]
