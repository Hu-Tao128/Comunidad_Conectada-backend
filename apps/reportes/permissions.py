from rest_framework.permissions import IsAuthenticated, SAFE_METHODS

from apps.communities.models import PrivadaMiembro, RolPrivada


class ReportesReadPermission(IsAuthenticated):
    """Autoriza operaciones de reportes sin alterar permisos globales."""

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        if request.user.is_staff or obj.creador_id == request.user.id:
            return True

        return PrivadaMiembro.objects.filter(
            privada=obj.privada,
            usuario=request.user,
            rol=RolPrivada.MODERADOR,
            status="activo",
            deleted_at__isnull=True,
        ).exists()

