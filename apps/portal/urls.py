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
]
