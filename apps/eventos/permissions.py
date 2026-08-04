from rest_framework.permissions import IsAuthenticated


class EventoPermission(IsAuthenticated):
    """La autorización por rol se valida contra la privada en la vista."""
