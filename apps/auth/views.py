"""Vistas para autenticación."""

from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import TokenObtainPairEmailSerializer


class TokenObtainPairEmailView(TokenObtainPairView):
    """Vista para obtener token JWT usando email en lugar de username."""

    serializer_class = TokenObtainPairEmailSerializer
