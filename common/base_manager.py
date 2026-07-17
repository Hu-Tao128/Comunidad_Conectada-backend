from .managers import ActiveManager, AllObjectsManager, SoftDeleteQuerySet

BaseManager = ActiveManager
SoftDeleteManager = AllObjectsManager

__all__ = ("BaseManager", "SoftDeleteManager", "SoftDeleteQuerySet")
