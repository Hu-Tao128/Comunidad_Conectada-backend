from rest_framework import serializers

from .models import Perfil, Usuario


class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ("id", "username", "first_name", "last_name", "email", "status", "is_active", "date_joined")


class PerfilSerializer(serializers.ModelSerializer):
    class Meta:
        model = Perfil
        fields = ("usuario", "nombres", "apellidos", "numero_casa", "rol", "telefono", "casa", "avatar", "bio")
