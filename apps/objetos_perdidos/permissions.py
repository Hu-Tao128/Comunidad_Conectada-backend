from rest_framework.permissions import IsAuthenticated


class ObjetosPerdidosPermission(IsAuthenticated):
    """El alcance por privada y los roles se validan en cada vista/acción."""
