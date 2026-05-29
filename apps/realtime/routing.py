from django.urls import re_path
from .consumers import CuotasConsumer

websocket_urlpatterns = [
    # Usamos .as_asgi() que es el método nativo para los Consumers asíncronos
    re_path(r'ws/cuotas/$', CuotasConsumer.as_asgi()),
]