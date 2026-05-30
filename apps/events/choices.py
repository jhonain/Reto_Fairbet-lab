from django.db import models

class EstadoEvento(models.TextChoices):
    PROGRAMADO = ('programado', 'Programado')
    EN_VIVO = ('en_vivo', 'En vivo')
    FINALIZADO = ('finalizado', 'Finalizado')
    SUSPENDIDO = ('suspendido', 'Suspendido')
    ANULADO = ('anulado', 'Anulado')

class TipoMercado(models.TextChoices):
    UNO_X_DOS = ('1x2', '1X2 (Resultado final)')
    SOBRE_BAJO = ('sobre_bajo', 'Más o menos de 2.5 goles')
    AMBOS_ANOTAN = ('ambos_anotan', 'Ambos equipos anotan')
    HANDICAP_ASIATICO = ('handicap_asiatico', 'Hándicap asiático')
    OVER_UNDER_25 = ('OVER_UNDER_25', 'Más o menos de 2.5 goles')
    BTTS = ('BTTS', 'Ambos equipos anotan')

class EstadoMercado(models.TextChoices):
    ABIERTO = ('abierto', 'Abierto')
    SUSPENDIDO = ('suspendido', 'Suspendido')
    CERRADO = ('cerrado', 'Cerrado')
    LIQUIDADO = ('liquidado', 'Liquidado')

class CodigoSeleccion(models.TextChoices):
    LOCAL = ('local', 'Gana el local')
    EMPATE = ('empate', 'Empate')
    VISITANTE = ('visitante', 'Gana la visita')
    SOBRE = ('sobre', 'Más de 2.5 goles')
    BAJO = ('bajo', 'Menos de 2.5 goles')
    SI = ('si', 'Sí, ambos anotan')
    NO = ('no', 'No, no anotan los dos')
    OVER25 = ('OVER25', 'Más de 2.5 goles')
    UNDER25 = ('UNDER25', 'Menos de 2.5 goles')
    BTTS_SI = ('BTTS_SI', 'Sí, ambos anotan')
    BTTS_NO = ('BTTS_NO', 'No, no anotan los dos')
    HA_L_05 = ('HA_L_05', 'Hándicap: gana el local')
    HA_V_05 = ('HA_V_05', 'Hándicap: gana la visita')

class MotivoSuspension(models.TextChoices):
    EVENTO_CRITICO = ('evento_critico', 'Evento crítico (gol, expulsión)')
    MANUAL = ('manual', 'Suspensión manual del operador')
    PRE_PARTIDO = ('pre_partido', 'Cierre pre-partido')
    LIQUIDACION = ('liquidacion', 'Liquidación en curso')
