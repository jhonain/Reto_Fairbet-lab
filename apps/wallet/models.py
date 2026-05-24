import uuid
from decimal import Decimal
from django.db import models, transaction
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from .choices import TipoCuenta, DireccionAsiento, TipoAsiento


Usuario = get_user_model()



class Cuenta(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="cuentas",
        help_text="Null para cuentas del sistema (casa, pendientes, bonos)",
        verbose_name="Usuario"
    )
    tipo_cuenta = models.CharField(
        max_length=30,
        choices=TipoCuenta.choices,
        verbose_name="Tipo de cuenta"
    )
    moneda = models.CharField(
        max_length=3,
        default="FIC",
        help_text="FIC = Fichas virtuales",
        verbose_name="Moneda"
    )
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de creación"
    )

    class Meta:
        db_table = "billetera_cuenta"
        unique_together = [["usuario", "tipo_cuenta"]]
        verbose_name = "Cuenta"
        verbose_name_plural = "Cuentas"

    def __str__(self):
        return f"{self.tipo_cuenta} [{self.usuario or 'SISTEMA'}]"

    @property
    def saldo(self) -> Decimal:
        resultado = self.asientos.aggregate(
            creditos=models.Sum(
                "monto",
                filter=models.Q(direccion=DireccionAsiento.CREDITO)
            ),
            debitos=models.Sum(
                "monto",
                filter=models.Q(direccion=DireccionAsiento.DEBITO)
            ),
        )
        creditos = resultado["creditos"] or Decimal("0")
        debitos = resultado["debitos"] or Decimal("0")
        return creditos - debitos

    def obtener_saldo_con_bloqueo(self) -> Decimal:
        asientos = self.asientos.select_for_update().all()
        creditos = sum(
            a.monto for a in asientos
            if a.direccion == DireccionAsiento.CREDITO
        )
        debitos = sum(
            a.monto for a in asientos
            if a.direccion == DireccionAsiento.DEBITO
        )
        return creditos - debitos


class AsientoContable(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cuenta = models.ForeignKey(
        Cuenta,
        on_delete=models.PROTECT,
        related_name="asientos",
        verbose_name="Cuenta"
    )
    monto = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        verbose_name="Monto"
    )
    direccion = models.CharField(
        max_length=10,
        choices=DireccionAsiento.choices,
        verbose_name="Dirección"
    )
    id_transaccion = models.UUIDField(
        db_index=True,
        verbose_name="ID de transacción"
    )
    tipo_asiento = models.CharField(
        max_length=20,
        choices=TipoAsiento.choices,
        verbose_name="Tipo de asiento"
    )
    id_referencia = models.UUIDField(
        null=True,
        blank=True,
        verbose_name="ID de referencia"
    )
    notas = models.TextField(blank=True, verbose_name="Notas")
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name="Fecha de creación"
    )

    class Meta:
        db_table = "billetera_asiento"
        ordering = ["fecha_creacion"]
        verbose_name = "Asiento contable"
        verbose_name_plural = "Asientos contables"
        indexes = [
            models.Index(fields=["id_transaccion"]),
            models.Index(fields=["cuenta", "fecha_creacion"]),
        ]

    def clean(self):
        if self.monto <= Decimal("0"):
            raise ValidationError("El monto debe ser positivo.")

    def save(self, *args, **kwargs):
        if self.pk:
            raise ValidationError("Los asientos son inmutables.")
        self.clean()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError("Los asientos son inmutables.")


class ServicioBilletera:
    @staticmethod
    @transaction.atomic
    def recargar(usuario, monto: Decimal, clave_idempotencia: uuid.UUID):
        if AsientoContable.objects.filter(id_transaccion=clave_idempotencia).exists():
            return

        cuenta_usuario = Cuenta.objects.select_for_update().get(
            usuario=usuario,
            tipo_cuenta=TipoCuenta.BILLETERA_USUARIO
        )
        cuenta_casa = Cuenta.objects.select_for_update().get(
            tipo_cuenta=TipoCuenta.CASA,
            usuario__isnull=True
        )

        AsientoContable.objects.create(
            cuenta=cuenta_usuario,
            monto=monto,
            direccion=DireccionAsiento.CREDITO,
            id_transaccion=clave_idempotencia,
            tipo_asiento=TipoAsiento.RECARGA,
        )
        AsientoContable.objects.create(
            cuenta=cuenta_casa,
            monto=monto,
            direccion=DireccionAsiento.DEBITO,
            id_transaccion=clave_idempotencia,
            tipo_asiento=TipoAsiento.RECARGA,
        )

    @staticmethod
    @transaction.atomic
    def bloquear_para_apuesta(usuario, monto: Decimal, id_apuesta: uuid.UUID, clave_idempotencia: uuid.UUID):
        if AsientoContable.objects.filter(id_transaccion=clave_idempotencia).exists():
            return

        cuenta_usuario = Cuenta.objects.select_for_update().get(
            usuario=usuario,
            tipo_cuenta=TipoCuenta.BILLETERA_USUARIO
        )
        cuenta_pendientes = Cuenta.objects.select_for_update().get(
            tipo_cuenta=TipoCuenta.APUESTAS_PENDIENTES,
            usuario__isnull=True
        )

        saldo = cuenta_usuario.obtener_saldo_con_bloqueo()
        if saldo < monto:
            raise ValidationError(f"Saldo insuficiente: {saldo}")

        AsientoContable.objects.create(
            cuenta=cuenta_usuario,
            monto=monto,
            direccion=DireccionAsiento.DEBITO,
            id_transaccion=clave_idempotencia,
            tipo_asiento=TipoAsiento.BLOQUEO_APUESTA,
            id_referencia=id_apuesta,
        )
        AsientoContable.objects.create(
            cuenta=cuenta_pendientes,
            monto=monto,
            direccion=DireccionAsiento.CREDITO,
            id_transaccion=clave_idempotencia,
            tipo_asiento=TipoAsiento.BLOQUEO_APUESTA,
            id_referencia=id_apuesta,
        )