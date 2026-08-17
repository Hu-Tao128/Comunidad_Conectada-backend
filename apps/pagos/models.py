"""Cuotas y pagos de la comunidad."""

from django.core.validators import MinValueValidator
from django.db import models

from apps.accounts.models import Usuario
from apps.communities.models import Privada
from common.models import BaseModel
from common.choices import EstadoIntentoPago, EstadoPago


class TipoCuota(models.TextChoices):
    MENSUAL = "mensual", "Mensual"
    UNICO = "unico", "Único"


class Cuota(BaseModel):
    """Cargo periódico o extraordinario de una privada."""

    privada = models.ForeignKey(Privada, on_delete=models.PROTECT, related_name="cuotas")
    clave = models.CharField(max_length=80, unique=True)
    cuenta = models.CharField(max_length=120, blank=True)
    categoria = models.CharField(max_length=80, blank=True)
    descripcion = models.TextField(blank=True)
    nombre = models.CharField(max_length=180)
    monto = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0.01)])
    fecha_vencimiento = models.DateField(db_index=True)
    tipo_pago = models.CharField(max_length=20, choices=TipoCuota.choices, default=TipoCuota.UNICO)
    icono = models.CharField(max_length=50, blank=True)
    color_icono = models.CharField(max_length=30, blank=True)

    class Meta:
        verbose_name = "cuota"
        verbose_name_plural = "cuotas"
        ordering = ("-fecha_vencimiento",)
        indexes = [models.Index(fields=("privada", "fecha_vencimiento"))]

    def __str__(self) -> str:
        return f"{self.nombre} - {self.monto}"


class Pago(BaseModel):
    """Pago aplicado a una cuota."""

    cuota = models.ForeignKey(Cuota, on_delete=models.PROTECT, related_name="pagos")
    pagador = models.ForeignKey(Usuario, on_delete=models.PROTECT, related_name="pagos")
    privada = models.ForeignKey(Privada, on_delete=models.PROTECT, related_name="pagos")
    estado = models.CharField(max_length=20, choices=EstadoPago.choices, default=EstadoPago.PENDIENTE, db_index=True)
    fecha_pago = models.DateTimeField(null=True, blank=True)
    fecha_validacion = models.DateTimeField(null=True, blank=True)
    validador = models.ForeignKey(Usuario, on_delete=models.PROTECT, related_name="pagos_validados", null=True, blank=True)
    comprobante_url = models.URLField(max_length=500, blank=True)

    class Meta:
        verbose_name = "pago"
        verbose_name_plural = "pagos"
        ordering = ("-created_at",)
        indexes = [models.Index(fields=("cuota", "estado"))]
        constraints = [models.UniqueConstraint(fields=("cuota", "pagador"), name="uq_pago_cuota_pagador")]
        permissions = (("can_validate_payments", "Can validate payments"),)

    def __str__(self) -> str:
        return f"{self.pagador} - {self.cuota}"


class PagoIntento(BaseModel):
    """Historial inmutable de comprobantes enviados y revisados."""

    pago = models.ForeignKey(Pago, on_delete=models.CASCADE, related_name="intentos")
    comprobante_url = models.URLField(max_length=500)
    estado = models.CharField(max_length=20, choices=EstadoIntentoPago.choices, default=EstadoIntentoPago.EN_REVISION, db_index=True)
    enviado_en = models.DateTimeField(auto_now_add=True)
    revisado_en = models.DateTimeField(null=True, blank=True)
    validador = models.ForeignKey(Usuario, on_delete=models.PROTECT, related_name="intentos_pago_validados", null=True, blank=True)
    motivo_declinado = models.TextField(blank=True)

    class Meta:
        ordering = ("-enviado_en",)
        indexes = [models.Index(fields=("pago", "estado"), name="pagos_pagoi_pago_id_4e0b40_idx")]

    def __str__(self) -> str:
        return f"Intento {self.pago_id} - {self.estado}"
