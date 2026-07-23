"""Entidades estructurales de la comunidad."""

import secrets
import string

from django.db import models

from common.models import BaseModel


def generar_codigo_privada() -> str:
    """Genera un código corto y legible para invitar a una privada."""
    alphabet = string.ascii_uppercase + string.digits
    return "CC-" + "".join(secrets.choice(alphabet) for _ in range(8))


class RolPrivada(models.TextChoices):
    HABITANTE = "habitante", "Habitante"
    MODERADOR = "moderador", "Moderador"


class Privada(BaseModel):
    """Comunidad residencial."""

    codigo = models.CharField(max_length=30, unique=True, default=generar_codigo_privada)
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


class PrivadaMiembro(BaseModel):
    """Relación de un usuario con una privada y su rol dentro de ella."""

    privada = models.ForeignKey(Privada, on_delete=models.CASCADE, related_name="miembros")
    usuario = models.ForeignKey("accounts.Usuario", on_delete=models.CASCADE, related_name="membresias_privada")
    rol = models.CharField(max_length=12, choices=RolPrivada.choices, default=RolPrivada.HABITANTE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=("privada", "usuario"), name="uq_miembro_privada_usuario"),
        ]
        ordering = ("privada__nombre", "usuario__username")

    def __str__(self) -> str:
        return f"{self.usuario} - {self.privada} ({self.rol})"


class ModuloSistema(BaseModel):
    """Funcionalidad que puede contratar una privada y aparecer en el sidebar."""

    codigo = models.SlugField(max_length=60, unique=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    activo = models.BooleanField(default=True)
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ("orden", "nombre")

    def __str__(self) -> str:
        return self.nombre


class PrivadaModulo(BaseModel):
    """Módulo del sistema contratado por una privada."""

    privada = models.ForeignKey(Privada, on_delete=models.CASCADE, related_name="modulos_contratados")
    modulo = models.ForeignKey(ModuloSistema, on_delete=models.PROTECT, related_name="privadas")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=("privada", "modulo"), name="uq_privada_modulo_sistema"),
        ]


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
