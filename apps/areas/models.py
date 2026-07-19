"""Áreas comunes y sus reservas."""

from django.core.validators import MinValueValidator
from django.db import models

from apps.communities.models import Privada
from common.models import BaseModel


class AreaComunitaria(BaseModel):
    """Espacio común que puede ser reservado."""

    privada = models.ForeignKey(Privada, on_delete=models.PROTECT, related_name="areas")
    codigo = models.CharField(max_length=30, unique=True)
    nombre = models.CharField(max_length=120)
    descripcion = models.TextField(blank=True)
    capacidad = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    imagen = models.ImageField(upload_to="areas/", blank=True)

    class Meta:
        verbose_name = "área comunitaria"
        verbose_name_plural = "áreas comunitarias"
        ordering = ("nombre",)
        constraints = [models.UniqueConstraint(fields=("privada", "nombre"), name="uq_area_privada_nombre")]

    def __str__(self) -> str:
        return self.nombre
