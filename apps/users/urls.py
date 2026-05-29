from django.urls import path
from .views import RegistroView, VerificarKYCView, PerfilView

urlpatterns = [
    path("registro/", RegistroView.as_view(), name="registro"),
    path("perfil/", PerfilView.as_view(), name="perfil"),
    path("verificar-kyc/", VerificarKYCView.as_view(), name="verificar-kyc"),
]
