"""Permisos compartidos."""

from rest_framework.permissions import IsAuthenticated


class ReadOnlyAuthenticated(IsAuthenticated):
    """Requiere autenticación para consultar recursos."""

