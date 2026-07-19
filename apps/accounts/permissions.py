from common.permissions import ReadOnlyAuthenticated


class AccountsReadPermission(ReadOnlyAuthenticated):
    """Permiso de consulta para cuentas y privadas."""

