"""Vistas para cuentas de usuario."""

from rest_framework import generics
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from common.mixins import ReadOnlyViewSet
from .models import Usuario

from .filters import UsuarioFilter
from .permissions import AccountsReadPermission
from .serializers import UsuarioSerializer, PerfilSerializer


class UsuarioViewSet(ReadOnlyViewSet):
    queryset = Usuario.objects.filter(status="activo", is_active=True).select_related("perfil")
    serializer_class = UsuarioSerializer
    permission_classes = (AccountsReadPermission,)
    filterset_class = UsuarioFilter
    search_fields = ("username", "first_name", "last_name", "email")
    ordering_fields = ("username", "date_joined")


class UsuarioMeView(generics.RetrieveAPIView):
    """Vista para obtener el usuario autenticado."""

    serializer_class = UsuarioSerializer
    permission_classes = (AccountsReadPermission,)
    authentication_classes = (JWTAuthentication,)

    def get_object(self):
        return self.request.user
