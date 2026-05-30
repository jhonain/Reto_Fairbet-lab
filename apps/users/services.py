from django.db.models import Q
from django.utils import timezone
from apps.users.choices import EstadoKYC

def obtener_estado_operativo(usuario):
    perfil = getattr(usuario, 'perfil', None)
    if perfil is None:
        return {'puede_apostar': False, 'estado_kyc': 'sin_perfil', 'motivo': 'No tienes perfil KYC registrado.', 'tiene_perfil': False, 'tiene_autoexclusion_activa': False}
    tiene_autoexclusion_activa = usuario.exclusiones.filter(activa=True).filter(Q(fecha_fin__isnull=True) | Q(fecha_fin__gt=timezone.now())).exists()
    if perfil.estado_kyc == EstadoKYC.BLOQUEADO:
        motivo = 'Tu cuenta esta bloqueada.'
    elif perfil.estado_kyc != EstadoKYC.VERIFICADO:
        motivo = 'Tu cuenta esta pendiente de verificacion KYC.'
    elif tiene_autoexclusion_activa:
        motivo = 'No puedes apostar por autoexclusion activa.'
    else:
        motivo = 'Tu cuenta esta habilitada para apostar.'
    return {'puede_apostar': perfil.puede_apostar, 'estado_kyc': perfil.estado_kyc, 'motivo': motivo, 'tiene_perfil': True, 'tiene_autoexclusion_activa': tiene_autoexclusion_activa}
