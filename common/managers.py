"""Managers que respetan el borrado lógico."""

from django.db import models


class SoftDeleteQuerySet(models.QuerySet):
    """Convierte delete masivo en desactivación masiva."""

    def delete(self) -> tuple[int, dict[str, int]]:
        updated = self.update(status="eliminado", deleted_at=models.functions.Now())
        return updated, {self.model._meta.label: updated}


class ActiveManager(models.Manager.from_queryset(SoftDeleteQuerySet)):
    """Retorna únicamente registros activos."""

    def get_queryset(self) -> models.QuerySet:
        return super().get_queryset().filter(status="activo", deleted_at__isnull=True)


class AllObjectsManager(models.Manager.from_queryset(SoftDeleteQuerySet)):
    """Manager para inspección administrativa de registros inactivos."""
