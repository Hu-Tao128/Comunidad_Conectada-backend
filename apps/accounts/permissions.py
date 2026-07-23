from common.permissions import ReadOnlyAuthenticated
from apps.communities.models import PrivadaMiembro, RolPrivada


class AccountsReadPermission(ReadOnlyAuthenticated):
    """Permiso de consulta para cuentas y privadas."""


class ModeratorPermission(ReadOnlyAuthenticated):
    """Permite operaciones del panel únicamente a admins o moderadores."""

    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        return request.user.is_staff or PrivadaMiembro.objects.filter(
            usuario=request.user,
            rol=RolPrivada.MODERADOR,
            status="activo",
            deleted_at__isnull=True,
        ).exists()
