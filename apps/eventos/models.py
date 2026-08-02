"""Eventos organizados dentro de una privada."""

from django.core.exceptions import ValidationError
from django.db import models

from apps.communities.models import Privada
from common.models import BaseModel


class Evento(BaseModel):
    """Actividad publicada para los miembros de una privada."""

    privada = models.ForeignKey(Privada, on_delete=models.PROTECT, related_name="eventos")
    titulo = models.CharField(max_length=180)
    descripcion = models.TextField(blank=True)
    fecha_inicio = models.DateTimeField(db_index=True)
    fecha_fin = models.DateTimeField(null=True, blank=True)
    ubicacion = models.CharField(max_length=255, blank=True)
    capacidad = models.PositiveIntegerField(null=True, blank=True)
    imagen = models.ImageField(upload_to="eventos/", blank=True)

    class Meta:
        verbose_name = "evento"
        verbose_name_plural = "eventos"
        ordering = ("fecha_inicio", "titulo")
        indexes = [models.Index(fields=("privada", "fecha_inicio"))]

    def clean(self):
        if self.fecha_fin and self.fecha_fin < self.fecha_inicio:
            raise ValidationError({"fecha_fin": "La fecha final debe ser posterior a la inicial."})

    def __str__(self):
        return self.titulo
