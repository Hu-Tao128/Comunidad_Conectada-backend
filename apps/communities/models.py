"""Entidades estructurales de la comunidad."""

from django.db import models

from common.models import BaseModel


class Privada(BaseModel):
    """Comunidad residencial."""

    codigo = models.CharField(max_length=30, unique=True)
    nombre = models.CharField(max_length=150)
    dir_num_exterior = models.CharField(max_length=20, blank=True)
    dir_colonia = models.CharField(max_length=100, blank=True)
    dir_calle = models.CharField(max_length=150, blank=True)
    dir_cp = models.CharField(max_length=10, blank=True)
    dir_ciudad = models.CharField(max_length=100, blank=True)
    dir_estado = models.CharField(max_length=100, blank=True)
    creador = models.ForeignKey("accounts.Usuario", on_delete=models.PROTECT, related_name="privadas_creadas")

    class Meta:
        verbose_name = "privada"
        verbose_name_plural = "privadas"
        ordering = ("nombre",)

    def __str__(self) -> str:
        return self.nombre


class Modulo(BaseModel):
    """Módulo de una privada."""

    privada = models.ForeignKey(Privada, on_delete=models.PROTECT, related_name="modulos")
    nombre = models.CharField(max_length=100)

    class Meta:
        constraints = [models.UniqueConstraint(fields=("privada", "nombre"), name="uq_modulo_privada_nombre")]
        ordering = ("nombre",)

    def __str__(self) -> str:
        return self.nombre


class Casa(BaseModel):
    """Casa perteneciente a un módulo."""

    modulo = models.ForeignKey(Modulo, on_delete=models.PROTECT, related_name="casas")
    numero = models.CharField(max_length=30)

    class Meta:
        constraints = [models.UniqueConstraint(fields=("modulo", "numero"), name="uq_casa_modulo_numero")]
        ordering = ("numero",)

    def __str__(self) -> str:
        return f"{self.modulo} - {self.numero}"
