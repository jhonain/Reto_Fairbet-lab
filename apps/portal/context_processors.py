from django.conf import settings
from apps.responsible_gaming.constants import MENSAJE_CONSUMO_RESPONSABLE

def aviso_legal(request):
    return {'aviso_legal': settings.FAIRBET_AVISO_LEGAL, 'mensaje_juego_responsable': MENSAJE_CONSUMO_RESPONSABLE}
