"""Modelos compartidos de la aplicación."""

import uuid

from django.conf import settings
from django.db import models

from common.managers import ActiveManager, AllObjectsManager


class RecordStatus(models.TextChoices):
    ACTIVO = "activo", "Activo"
    SUSPENDIDO = "suspendido", "Suspendido"
    ELIMINADO = "eliminado", "Eliminado"

class BaseModel(models.Model):
    """Modelo base con UUID, auditoría y soporte de borrado lógico."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=12, choices=RecordStatus.choices, default=RecordStatus.ACTIVO, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True, db_index=True)
    created_ip = models.GenericIPAddressField(null=True, blank=True)
    updated_ip = models.GenericIPAddressField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name="%(app_label)s_%(class)s_created", null=True, blank=True,
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name="%(app_label)s_%(class)s_updated", null=True, blank=True,
    )
    objects = ActiveManager()
    all_objects = AllObjectsManager()

    class Meta:
        abstract = True
        ordering = ("-created_at",)

    def delete(self, using: str | None = None, keep_parents: bool = False) -> tuple[int, dict[str, int]]:
        """Desactiva el registro en lugar de borrarlo físicamente."""
        self.status = RecordStatus.ELIMINADO
        self.deleted_at = models.functions.Now()
        self.save(update_fields=("status", "deleted_at", "updated_at"), using=using)
        return 1, {self._meta.label: 1}
