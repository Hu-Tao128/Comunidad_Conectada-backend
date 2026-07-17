"""Usuarios y perfiles de la comunidad."""

import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models

from common.models import RecordStatus


class Usuario(AbstractUser):
    """Usuario de Django con UUID como identificador principal."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, db_index=True)
    status = models.CharField(max_length=12, choices=RecordStatus.choices, default=RecordStatus.ACTIVO, db_index=True)

    class Meta:
        verbose_name = "usuario"
        verbose_name_plural = "usuarios"
        ordering = ("username",)
        permissions = (("can_manage_users", "Can manage users"),)

    def __str__(self) -> str:
        return self.get_full_name() or self.username


class Perfil(models.Model):
    """Información pública adicional asociada a un usuario."""

    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name="perfil")
    nombres = models.CharField(max_length=100, blank=True)
    apellidos = models.CharField(max_length=150, blank=True)
    numero_casa = models.CharField(max_length=30, blank=True)
    rol = models.CharField(max_length=80, blank=True)
    telefono = models.CharField(max_length=30, blank=True)
    casa = models.ForeignKey("communities.Casa", on_delete=models.PROTECT, related_name="perfiles", null=True, blank=True)
    avatar = models.ImageField(upload_to="perfiles/", blank=True)
    bio = models.TextField(blank=True)

    class Meta:
        verbose_name = "perfil"
        verbose_name_plural = "perfiles"

    def __str__(self) -> str:
        return f"Perfil de {self.usuario}"
