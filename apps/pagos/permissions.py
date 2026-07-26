from rest_framework.permissions import BasePermission, SAFE_METHODS

from apps.communities.models import PrivadaMiembro, RolPrivada


class PagosPermission(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if view.basename == "cuota" and request.method not in SAFE_METHODS:
            return request.user.is_staff or PrivadaMiembro.objects.filter(
                usuario=request.user, rol=RolPrivada.MODERADOR, status="activo", deleted_at__isnull=True
            ).exists()
        return True
