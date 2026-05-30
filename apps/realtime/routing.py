from django.urls import re_path
from .consumers import CuotasConsumer
websocket_urlpatterns = [re_path('ws/cuotas/$', CuotasConsumer.as_asgi())]
