"""Directorio de proveedores y servicios."""

from django.db import models

from apps.communities.models import Privada
from common.models import BaseModel


class Directorio(BaseModel):
    """Entrada pública del directorio de la comunidad."""

    privada = models.ForeignKey(Privada, on_delete=models.PROTECT, related_name="directorio")
    nombre = models.CharField(max_length=150)
    categorias = models.CharField(max_length=150, db_index=True)
    descripcion = models.TextField(blank=True)
    num_tel = models.CharField(max_length=30, blank=True)
    codigo = models.CharField(max_length=50, blank=True)
    ubicacion = models.CharField(max_length=255, blank=True)
    imagenes = models.ImageField(upload_to="directorio/", blank=True)

    class Meta:
        verbose_name = "entrada del directorio"
        verbose_name_plural = "entradas del directorio"
        ordering = ("nombre",)
        constraints = [models.UniqueConstraint(fields=("privada", "nombre"), name="uq_directorio_privada_nombre")]
        indexes = [models.Index(fields=("privada", "categorias"))]
        permissions = (("can_create_directory", "Can create directory"),)

    def __str__(self) -> str:
        return self.nombre
