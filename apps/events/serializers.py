from rest_framework import serializers
from .models import Evento, Mercado, Cuota, HistorialCuota

class CuotaSerializer(serializers.ModelSerializer):
    # Forzamos a que el JSON devuelva el string con la precisión exacta
    valor = serializers.DecimalField(max_digits=10, decimal_places=4)

    class Meta:
        model = Cuota
        fields = ['id', 'seleccion', 'valor', 'activa', 'es_ganadora']


class MercadoSerializer(serializers.ModelSerializer):
    cuotas = CuotaSerializer(many=True, read_only=True)

    class Meta:
        model = Mercado
        fields = ['id', 'tipo', 'estado', 'margen_operador', 'cuotas']


class EventoSerializer(serializers.ModelSerializer):
    mercados = MercadoSerializer(many=True, read_only=True)
    estan_apuestas_abiertas = serializers.BooleanField(read_only=True)

    class Meta:
        model = Evento
        fields = [
            'id', 'nombre', 'deporte', 'equipo_local', 'equipo_visitante', 
            'inicia_en', 'estado', 'resultado', 'estan_apuestas_abiertas',
            'es_momento_critico', 'desempate_fair_play', 'mercados'
        ]