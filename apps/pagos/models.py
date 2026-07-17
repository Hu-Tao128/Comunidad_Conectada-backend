"""Cuotas y pagos de la comunidad."""

from django.core.validators import MinValueValidator
from django.db import models

from apps.accounts.models import Usuario
from apps.communities.models import Privada
from common.models import BaseModel


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

    class Meta:
        verbose_name = "cuota"
        verbose_name_plural = "cuotas"
        ordering = ("-fecha_vencimiento",)
        indexes = [models.Index(fields=("privada", "fecha_vencimiento"))]

    def __str__(self) -> str:
        return f"{self.nombre} - {self.monto}"


class Pago(BaseModel):
    """Pago aplicado a una cuota."""

    class Estado(models.TextChoices):
        PENDIENTE = "pendiente", "Pendiente"
        APROBADO = "aprobado", "Aprobado"
        RECHAZADO = "rechazado", "Rechazado"

    cuota = models.ForeignKey(Cuota, on_delete=models.PROTECT, related_name="pagos")
    pagador = models.ForeignKey(Usuario, on_delete=models.PROTECT, related_name="pagos")
    privada = models.ForeignKey(Privada, on_delete=models.PROTECT, related_name="pagos")
    monto = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0.01)])
    num = models.PositiveIntegerField(unique=True)
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.PENDIENTE, db_index=True)
    pagado_en = models.DateTimeField(null=True, blank=True)
    fecha_pago = models.DateTimeField(null=True, blank=True)
    fecha_validacion = models.DateTimeField(null=True, blank=True)
    validador = models.ForeignKey(Usuario, on_delete=models.PROTECT, related_name="pagos_validados", null=True, blank=True)
    comprobante = models.ImageField(upload_to="pagos/", blank=True)

    class Meta:
        verbose_name = "pago"
        verbose_name_plural = "pagos"
        ordering = ("-created_at",)
        indexes = [models.Index(fields=("cuota", "estado"))]
        permissions = (("can_validate_payments", "Can validate payments"),)

    def __str__(self) -> str:
        return str(self.num)
