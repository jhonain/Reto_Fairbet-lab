from django.db import models

class EstadoEvento(models.TextChoices):
    PROGRAMADO = "programado", "Programado"
    EN_VIVO = "en_vivo", "En vivo"
    FINALIZADO = "finalizado", "Finalizado"
    SUSPENDIDO = "suspendido", "Suspendido"
    ANULADO = "anulado", "Anulado"


class TipoMercado(models.TextChoices):
    UNO_X_DOS = "1x2", "1X2 (Resultado final)"
    SOBRE_BAJO = "sobre_bajo", "Over/Under 2.5 goles"
    AMBOS_ANOTAN = "ambos_anotan", "Ambos equipos anotan (BTTS)"
    HANDICAP_ASIATICO = "handicap_asiatico", "Hándicap asiático"


class EstadoMercado(models.TextChoices):
    ABIERTO = "abierto", "Abierto"
    SUSPENDIDO = "suspendido", "Suspendido"
    CERRADO = "cerrado", "Cerrado"
    LIQUIDADO = "liquidado", "Liquidado"


class CodigoSeleccion(models.TextChoices):
    # 1X2
    LOCAL = "local", "Gana local"
    EMPATE = "empate", "Empate"
    VISITANTE = "visitante", "Gana visitante"
    # Over/Under
    SOBRE = "sobre", "Over 2.5"
    BAJO = "bajo", "Under 2.5"
    # BTTS
    SI = "si", "Sí"
    NO = "no", "No"


class MotivoSuspension(models.TextChoices):
    EVENTO_CRITICO = "evento_critico", "Evento crítico (gol, expulsión)"
    MANUAL = "manual", "Suspensión manual del operador"
    PRE_PARTIDO = "pre_partido", "Cierre pre-partido"
    LIQUIDACION = "liquidacion", "Liquidación en curso"
