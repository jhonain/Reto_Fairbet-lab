import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

# 1. Configurar la variable de entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# 2. Inicializar la aplicación ASGI de Django para manejar HTTP tradicional
django_asgi_app = get_asgi_application()

# Importamos tus rutas de WebSockets creadas en el paso anterior
from apps.realtime.routing import websocket_urlpatterns

# 3. ProtocolTypeRouter se encarga de bifurcar el tráfico según el protocolo
application = ProtocolTypeRouter({
    # Tráfico HTTP tradicional (REST, Admin, Plantillas)
    "http": django_asgi_app,
    
    # Tráfico de WebSockets (Tiempo real para las cuotas)
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})