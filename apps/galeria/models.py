"""Galería de imágenes adicionales para las entidades del sistema."""

from django.db import models

from common.models import BaseModel


class GaleriaImagen(BaseModel):
    """Imagen adicional asociada a un directorio, evento u objeto perdido."""

    directorio = models.ForeignKey(
        "directorio.Directorio",
        on_delete=models.CASCADE,
        related_name="galeria",
        null=True,
        blank=True,
    )
    evento = models.ForeignKey(
        "eventos.Evento",
        on_delete=models.CASCADE,
        related_name="galeria",
        null=True,
        blank=True,
    )
    objeto = models.ForeignKey(
        "objetos_perdidos.ObjetoPerdido",
        on_delete=models.CASCADE,
        related_name="galeria",
        null=True,
        blank=True,
    )
    archivo = models.ImageField(upload_to="galeria/", max_length=500)
    orden = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name = "imagen de galería"
        verbose_name_plural = "imágenes de galería"
        ordering = ("orden", "created_at")
        constraints = [
            models.CheckConstraint(
                check=(
                    (
                        models.Q(directorio__isnull=False)
                        & models.Q(evento__isnull=True)
                        & models.Q(objeto__isnull=True)
                    )
                    | (
                        models.Q(directorio__isnull=True)
                        & models.Q(evento__isnull=False)
                        & models.Q(objeto__isnull=True)
                    )
                    | (
                        models.Q(directorio__isnull=True)
                        & models.Q(evento__isnull=True)
                        & models.Q(objeto__isnull=False)
                    )
                ),
                name="galeria_imagen_un_solo_dueno",
            )
        ]

    def __str__(self) -> str:
        for nombre in ("directorio", "evento", "objeto"):
            propietario = getattr(self, f"{nombre}_id", None)
            if propietario is not None:
                return f"{nombre}:{propietario} -> {self.archivo.name}"
        return str(self.archivo.name)
