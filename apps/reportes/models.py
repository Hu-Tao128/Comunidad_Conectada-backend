"""Reportes e incidentes de la comunidad."""

from django.core.validators import MinLengthValidator
from django.db import models

from apps.accounts.models import Usuario
from apps.communities.models import Privada
from common.models import BaseModel
from common.choices import Prioridad


class EstadoReporte(models.TextChoices):
    """Estados que puede tener un reporte dentro de este módulo."""

    PENDIENTE = "pendiente", "Pendiente"
    EN_PROCESO = "en_proceso", "En proceso"
    RESUELTO = "resuelto", "Resuelto"
    CONCLUIDO = "concluido", "Concluido"


class Reporte(BaseModel):
    """Reporte general creado por un usuario."""

    privada = models.ForeignKey(Privada, on_delete=models.PROTECT, related_name="reportes")
    num = models.PositiveIntegerField(unique=True)
    titulo = models.CharField(max_length=180)
    descripcion = models.TextField(validators=[MinLengthValidator(10)])
    tipo = models.CharField(max_length=80, blank=True)
    prioridad = models.CharField(max_length=30, choices=Prioridad.choices, default=Prioridad.MEDIA, blank=True)
    estado = models.CharField(max_length=20, choices=EstadoReporte.choices, default=EstadoReporte.PENDIENTE, db_index=True)
    fecha_suceso = models.DateField(null=True, blank=True)
    hora_suceso = models.TimeField(null=True, blank=True)
    evidencia = models.ImageField(upload_to="reportes/", blank=True)
    creador = models.ForeignKey(Usuario, on_delete=models.PROTECT, related_name="reportes_creados")
    supervisor = models.ForeignKey(Usuario, on_delete=models.PROTECT, related_name="reportes_supervisados", null=True, blank=True)

    class Meta:
        verbose_name = "reporte"
        verbose_name_plural = "reportes"
        ordering = ("-created_at",)
        indexes = [models.Index(fields=("privada", "estado"))]
        permissions = (("can_view_reports", "Can view reports"), ("can_manage_reports", "Can manage reports"),)

    def __str__(self) -> str:
        return self.titulo


class Incidente(BaseModel):
    """Detalle operativo opcional asociado a un reporte."""

    num = models.PositiveIntegerField(unique=True)
    reporte = models.ForeignKey(Reporte, on_delete=models.CASCADE, related_name="incidentes", null=True, blank=True)
    tipo = models.CharField(max_length=80, blank=True)
    ubicacion = models.CharField(max_length=255, blank=True)
    evidencia = models.ImageField(upload_to="incidentes/", blank=True)
    prioridad = models.CharField(max_length=30, blank=True)
    estado = models.CharField(max_length=30, blank=True)
    fecha_incidente = models.DateField(null=True, blank=True)
    fecha_registro = models.DateField(null=True, blank=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.PROTECT, related_name="incidentes")
    privada = models.ForeignKey(Privada, on_delete=models.PROTECT, related_name="incidentes")

    class Meta:
        verbose_name = "incidente"
        verbose_name_plural = "incidentes"
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"Incidente: {self.reporte.titulo}"
