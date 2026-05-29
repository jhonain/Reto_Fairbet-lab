from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EventoViewSet

# El Router genera automáticamente las rutas estándar para el CRUD
router = DefaultRouter()
router.register(r'', EventoViewSet, basename='evento')

urlpatterns = [
    path('', include(router.urls)),
]