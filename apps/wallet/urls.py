from django.urls import path
from .views import SaldoView, RecargaView, RetiroView, TransferenciaView

urlpatterns = [
    path("saldo/", SaldoView.as_view(), name="wallet-saldo"),
    path("recarga/", RecargaView.as_view(), name="wallet-recarga"),
    path("retiro/", RetiroView.as_view(), name="wallet-retiro"),
    path("transferencia/", TransferenciaView.as_view(), name="wallet-transferencia"),
]
