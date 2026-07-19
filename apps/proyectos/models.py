"""Proyectos de mejora comunitaria."""

from django.db import models

from apps.accounts.models import Usuario
from apps.communities.models import Privada
from common.models import BaseModel


class Proyecto(BaseModel):
    """Proyecto propuesto o ejecutado dentro de una privada."""

    class Estado(models.TextChoices):
        PROPUESTO = "propuesto", "Propuesto"
        APROBADO = "aprobado", "Aprobado"
        EN_PROGRESO = "en_progreso", "En progreso"
        COMPLETADO = "completado", "Completado"
        CANCELADO = "cancelado", "Cancelado"

    codigo = models.CharField(max_length=30, unique=True)
    privada = models.ForeignKey(Privada, on_delete=models.PROTECT, related_name="proyectos")
    nombre = models.CharField(max_length=180)
    descripcion = models.TextField()
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.PROPUESTO, db_index=True)
    capacidad = models.PositiveIntegerField(default=1)
    tipo = models.CharField(max_length=80, blank=True)
    fecha_inicio = models.DateField(null=True, blank=True)
    fecha_fin = models.DateField(null=True, blank=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.PROTECT, related_name="proyectos")

    class Meta:
        verbose_name = "proyecto"
        verbose_name_plural = "proyectos"
        ordering = ("-created_at",)
        constraints = [models.UniqueConstraint(fields=("privada", "nombre"), name="uq_proyecto_privada_nombre")]

    def __str__(self) -> str:
        return self.nombre
