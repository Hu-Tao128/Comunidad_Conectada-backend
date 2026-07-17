from rest_framework import serializers

from .models import Perfil, Usuario


class UsuarioSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.ReadOnlyField()

    class Meta:
        model = Usuario
        fields = ("id", "username", "first_name", "last_name", "nombre_completo", "email", "status", "is_active", "date_joined")


class PerfilSerializer(serializers.ModelSerializer):
    class Meta:
        model = Perfil
        fields = ("usuario", "nombres", "apellidos", "numero_casa", "telefono", "casa", "avatar", "bio")
