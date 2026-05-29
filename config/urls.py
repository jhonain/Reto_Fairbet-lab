"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings

class AvisoLegalView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        return Response({"aviso_legal": settings.FAIRBET_AVISO_LEGAL})


urlpatterns = [
    path('', include('apps.portal.urls')),
    path('admin/', admin.site.urls),
    path('api/aviso-legal/', AvisoLegalView.as_view()),
    path('api/usuarios/', include('apps.users.urls')),
    path('api/wallet/', include('apps.wallet.urls')),
    path('api/eventos/', include('apps.events.urls')),
    path('api/apuestas/', include('apps.betting.urls')),
    path('api/juego-responsable/', include('apps.responsible_gaming.urls')),
    # Operador
    path('api/operador/dashboard/', include('apps.dashboard.urls')),
]
