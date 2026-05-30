from django.contrib import admin
from django.urls import path, include
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings


class AvisoLegalView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        return Response({'aviso_legal': settings.FAIRBET_AVISO_LEGAL})


urlpatterns = [
    path('', include('apps.portal.urls')),
    path('admin/', admin.site.urls),
    path('api/aviso-legal/', AvisoLegalView.as_view()),
    path('api/usuarios/', include('apps.users.urls')),
    path('api/wallet/', include('apps.wallet.urls')),
    path('api/eventos/', include('apps.events.urls')),
    path('api/apuestas/', include('apps.betting.urls')),
    path('api/juego-responsable/', include('apps.responsible_gaming.urls')),
    path('operador/', include('apps.dashboard.urls')),
]
