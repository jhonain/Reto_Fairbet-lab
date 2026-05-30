from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Evento
from .choices import EstadoEvento, TipoMercado

class EventosListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        estado = request.query_params.get('estado', EstadoEvento.PROGRAMADO)
        eventos = Evento.objects.filter(estado=estado).order_by('inicia_en')[:50]
        data = []
        for ev in eventos:
            mercado = ev.mercados.filter(tipo=TipoMercado.UNO_X_DOS).first()
            cuotas = []
            if mercado:
                for c in mercado.cuotas.filter(activa=True):
                    cuotas.append({'id': str(c.id), 'seleccion': c.seleccion, 'valor': str(c.valor)})
            data.append({'id': str(ev.id), 'nombre': ev.nombre, 'equipo_local': ev.equipo_local, 'equipo_visitante': ev.equipo_visitante, 'inicia_en': ev.inicia_en.isoformat(), 'estado': ev.estado, 'cuotas_1x2': cuotas})
        return Response(data)