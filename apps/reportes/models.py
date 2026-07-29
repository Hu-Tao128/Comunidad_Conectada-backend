"""Reportes e incidentes de la comunidad."""

from django.core.validators import MinLengthValidator
from django.db import models
from django.utils import timezone

from apps.accounts.models import Usuario
from apps.communities.models import Privada
from common.models import BaseModel
from common.choices import EstadoIncidente, Prioridad


class EstadoReporte(models.TextChoices):
    """Estados que puede tener un reporte dentro de este módulo."""

    PENDIENTE = "pendiente", "Pendiente"
    EN_PROCESO = "en_proceso", "En proceso"
    RESUELTO = "resuelto", "Resuelto"
    CONCLUIDO = "concluido", "Concluido"


class TipoReporte(BaseModel):
    """Catálogo administrable compartido por incidentes y reportes."""

    nombre = models.CharField(max_length=80, unique=True)
    codigo = models.SlugField(max_length=80, unique=True)

    class Meta:
        ordering = ("nombre",)

    def __str__(self) -> str:
        return self.nombre


class Reporte(BaseModel):
    """Reporte general creado por un usuario."""

    privada = models.ForeignKey(Privada, on_delete=models.PROTECT, related_name="reportes")
    incidente = models.ForeignKey("Incidente", on_delete=models.PROTECT, related_name="reportes_seguimiento", null=True, blank=True)
    num = models.PositiveIntegerField(unique=True)
    titulo = models.CharField(max_length=180)
    descripcion = models.TextField(validators=[MinLengthValidator(10)])
    tipo = models.CharField(max_length=80, blank=True)
    tipo_categoria = models.ForeignKey(TipoReporte, on_delete=models.PROTECT, related_name="reportes", null=True, blank=True)
    prioridad = models.CharField(max_length=30, choices=Prioridad.choices, default=Prioridad.MEDIA, blank=True)
    estado = models.CharField(max_length=20, choices=EstadoReporte.choices, default=EstadoReporte.PENDIENTE, db_index=True)
    fecha_suceso = models.DateTimeField(null=True, blank=True)
    hora_suceso = models.TimeField(null=True, blank=True)
    evidencia = models.URLField(max_length=500, blank=True)
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
    titulo = models.CharField(max_length=180, default="Incidente")
    descripcion = models.TextField(default="Sin descripción", validators=[MinLengthValidator(10)])
    reporte = models.ForeignKey(Reporte, on_delete=models.CASCADE, related_name="incidentes", null=True, blank=True)
    tipo = models.CharField(max_length=80, blank=True)
    tipo_categoria = models.ForeignKey(TipoReporte, on_delete=models.PROTECT, related_name="incidentes", null=True, blank=True)
    ubicacion = models.CharField(max_length=255, blank=True)
    evidencia = models.URLField(max_length=500, blank=True)
    prioridad = models.CharField(max_length=30, choices=Prioridad.choices, default=Prioridad.MEDIA)
    estado = models.CharField(max_length=30, choices=EstadoIncidente.choices, default=EstadoIncidente.PENDIENTE, db_index=True)
    fecha_incidente = models.DateTimeField(null=True, blank=True)
    fecha_registro = models.DateTimeField(default=timezone.now, editable=False)
    usuario = models.ForeignKey(Usuario, on_delete=models.PROTECT, related_name="incidentes")
    privada = models.ForeignKey(Privada, on_delete=models.PROTECT, related_name="incidentes")

    class Meta:
        verbose_name = "incidente"
        verbose_name_plural = "incidentes"
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"Incidente #{self.num}: {self.titulo}"
