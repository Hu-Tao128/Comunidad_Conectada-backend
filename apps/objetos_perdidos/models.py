"""Objetos perdidos y encontrados."""

from django.db import models

from apps.accounts.models import Usuario
from apps.communities.models import Privada
from common.models import BaseModel


class ObjetoPerdido(BaseModel):
    """Registro de un objeto perdido dentro de la comunidad."""

    class Estado(models.TextChoices):
        PERDIDO = "perdido", "Perdido"
        ENCONTRADO = "encontrado", "Encontrado"
        ENTREGADO = "entregado", "Entregado"
        CERRADO = "cerrado", "Cerrado"

    privada = models.ForeignKey(Privada, on_delete=models.PROTECT, related_name="objetos_perdidos")
    reportado_por = models.ForeignKey(Usuario, on_delete=models.PROTECT, related_name="objetos_reportados")
    num = models.PositiveIntegerField(unique=True)
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField()
    tipo = models.CharField(max_length=80, blank=True)
    imagen = models.ImageField(upload_to="objetos_perdidos/", blank=True)
    fecha_reporte = models.DateField(null=True, blank=True)
    fecha_encontrado = models.DateField(null=True, blank=True)
    fecha_devuelto = models.DateField(null=True, blank=True)
    recuperador = models.ForeignKey(Usuario, on_delete=models.PROTECT, related_name="objetos_recuperados", null=True, blank=True)

    class Meta:
        verbose_name = "objeto perdido"
        verbose_name_plural = "objetos perdidos"
        ordering = ("-created_at",)
        indexes = [models.Index(fields=("privada", "tipo"))]

    def __str__(self) -> str:
        return self.nombre
