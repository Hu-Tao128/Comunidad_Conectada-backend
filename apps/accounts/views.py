"""Vistas para cuentas de usuario."""

from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from common.mixins import ReadOnlyViewSet
from .models import Perfil, Usuario
from apps.communities.models import PrivadaMiembro

from .filters import UsuarioFilter
from .permissions import AccountsReadPermission, ModeratorPermission
from .serializers import AdminUsuarioSerializer, CambiarPasswordSerializer, RegistroSerializer, UsuarioSerializer, PerfilSerializer


class UsuarioViewSet(ReadOnlyViewSet):
    queryset = Usuario.objects.filter(status="activo", is_active=True).select_related("perfil")
    serializer_class = UsuarioSerializer
    permission_classes = (ModeratorPermission,)
    filterset_class = UsuarioFilter
    search_fields = ("username", "first_name", "last_name", "email")
    ordering_fields = ("username", "date_joined")

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_staff:
            return queryset
        private_ids = PrivadaMiembro.objects.filter(
            usuario=self.request.user,
            status="activo",
            deleted_at__isnull=True,
        ).values("privada_id")
        return queryset.filter(
            membresias_privada__privada_id__in=private_ids,
            membresias_privada__status="activo",
            membresias_privada__deleted_at__isnull=True,
        ).distinct()


class UsuarioMeView(generics.RetrieveAPIView):
    """Vista para obtener el usuario autenticado."""

    serializer_class = UsuarioSerializer
    permission_classes = (AccountsReadPermission,)
    authentication_classes = (JWTAuthentication,)

    def get_object(self):
        return self.request.user


class RegistroView(APIView):
    """Registra un habitante y devuelve sus tokens para continuar en el lobby."""

    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = RegistroSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = TokenObtainPairSerializer.get_token(user)
        return Response(
            {
                "user": UsuarioSerializer(user).data,
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            status=status.HTTP_201_CREATED,
        )


class PerfilMeView(generics.RetrieveUpdateAPIView):
    """Consulta y actualiza el perfil del usuario autenticado."""

    serializer_class = PerfilSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def get_object(self):
        perfil, _ = Perfil.objects.get_or_create(usuario=self.request.user)
        return perfil


class AdminUsuariosView(generics.ListCreateAPIView):
    """Consulta y crea administradores globales de Comunidad Conectada."""

    queryset = Usuario.objects.filter(is_staff=True).order_by("username")
    serializer_class = AdminUsuarioSerializer
    permission_classes = (IsAdminUser,)
    authentication_classes = (JWTAuthentication,)


class CambiarPasswordView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def post(self, request):
        serializer = CambiarPasswordSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data["password"])
        request.user.save(update_fields=("password", "updated_at") if hasattr(request.user, "updated_at") else ("password",))
        return Response({"detail": "Contraseña actualizada correctamente."})
