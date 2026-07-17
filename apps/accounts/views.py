from common.mixins import ReadOnlyViewSet
from .models import Usuario

from .filters import UsuarioFilter
from .permissions import AccountsReadPermission
from .serializers import UsuarioSerializer


class UsuarioViewSet(ReadOnlyViewSet):
    queryset = Usuario.objects.filter(status="activo", is_active=True).select_related("perfil")
    serializer_class = UsuarioSerializer
    permission_classes = (AccountsReadPermission,)
    filterset_class = UsuarioFilter
    search_fields = ("username", "first_name", "last_name", "email")
    ordering_fields = ("username", "date_joined")
