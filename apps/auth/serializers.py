"""Serializers para autenticación."""

from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


class TokenObtainPairEmailSerializer(TokenObtainPairSerializer):
    """Serializer para obtener token JWT usando email en lugar de username."""

    username_field = "email"

    @classmethod
    def get_token(cls, user):
        """Obtener token para el usuario."""
        return super().get_token(user)

    def validate(self, attrs):
        """Validar credenciales y obtener token."""
        email = attrs.get("email")
        password = attrs.get("password")

        if email is None:
            raise serializers.ValidationError(_("Debe proporcionar el correo electrónico."))
        if password is None:
            raise serializers.ValidationError(_("Debe proporcionar la contraseña."))

        # Buscar usuario por email
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError(_("No se encontró un usuario con ese correo electrónico."))

        # Verificar contraseña
        if not user.check_password(password):
            raise serializers.ValidationError(_("Contraseña incorrecta."))

        # Verificar usuario activo
        if not user.is_active:
            raise serializers.ValidationError(_("El usuario está inactivo."))

        # Obtener token
        refresh = self.get_token(user)

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }
