import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from .validators import validar_dni, validar_edad
from .choices import EstadoKYC
Usuario = get_user_model()

class PerfilUsuario(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.OneToOneField(Usuario, on_delete=models.PROTECT, related_name='perfil')
    dni = models.CharField(max_length=8, unique=True, validators=[validar_dni], verbose_name='DNI')
    fecha_nacimiento = models.DateField(validators=[validar_edad], verbose_name='Fecha de nacimiento')
    estado_kyc = models.CharField(max_length=30, choices=EstadoKYC.choices, default=EstadoKYC.PENDIENTE, verbose_name='Estado KYC')
    fecha_verificacion_kyc = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de verificación KYC')
    telefono = models.CharField(max_length=9, blank=True, verbose_name='Teléfono')
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')

    class Meta:
        db_table = 'usuarios_perfil'
        verbose_name = 'Perfil de usuario'
        verbose_name_plural = 'Perfiles de usuario'

    def __str__(self):
        return f'{self.usuario.username} [{self.estado_kyc}]'

    @property
    def puede_apostar(self) -> bool:
        if self.estado_kyc == EstadoKYC.BLOQUEADO:
            return False
        if self.estado_kyc != EstadoKYC.VERIFICADO:
            return False
        tiene_exclusion_activa = self.usuario.exclusiones.filter(activa=True).filter(models.Q(fecha_fin__isnull=True) | models.Q(fecha_fin__gt=timezone.now())).exists()
        return not tiene_exclusion_activa

    def verificar(self):
        self.estado_kyc = EstadoKYC.VERIFICADO
        self.fecha_verificacion_kyc = timezone.now()
        self.save(update_fields=['estado_kyc', 'fecha_verificacion_kyc'])
