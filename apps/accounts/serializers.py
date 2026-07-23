import re
import uuid

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import Perfil, Usuario
from apps.communities.models import PrivadaMiembro

User = get_user_model()


class UsuarioSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.ReadOnlyField()
    perfil = serializers.SerializerMethodField()
    membresias = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()

    class Meta:
        model = Usuario
        fields = ("id", "username", "first_name", "last_name", "nombre_completo", "email", "status", "is_active", "date_joined", "perfil", "membresias", "role")

    def get_perfil(self, obj):
        try:
            return PerfilSerializer(obj.perfil).data
        except Perfil.DoesNotExist:
            return None

    def get_membresias(self, obj):
        return [
            {
                "id": str(m.id),
                "privada": str(m.privada_id),
                "privada_nombre": m.privada.nombre,
                "privada_codigo": m.privada.codigo,
                "rol": m.rol,
                "modulos_contratados": list(
                    m.privada.modulos_contratados.filter(
                        status="activo", deleted_at__isnull=True, modulo__activo=True
                    ).values_list("modulo__codigo", flat=True)
                ),
            }
            for m in PrivadaMiembro.objects.filter(
                usuario=obj,
                status="activo",
                deleted_at__isnull=True,
            ).select_related("privada")
        ]

    def get_role(self, obj):
        if obj.is_staff:
            return "admin"
        membership = PrivadaMiembro.objects.filter(
            usuario=obj,
            status="activo",
            deleted_at__isnull=True,
        ).order_by("-rol").first()
        return membership.rol if membership else "habitante"


class PerfilSerializer(serializers.ModelSerializer):
    class Meta:
        model = Perfil
        fields = ("id", "usuario", "nombres", "apellidos", "numero_casa", "codigo_postal", "telefono", "casa", "avatar", "bio")
        read_only_fields = ("id", "usuario", "casa")


class RegistroSerializer(serializers.Serializer):
    nombres = serializers.CharField(max_length=100)
    apellidos = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    telefono = serializers.CharField(max_length=30, required=False, allow_blank=True)
    numero_casa = serializers.CharField(max_length=30, required=False, allow_blank=True)
    codigo_postal = serializers.CharField(max_length=10, required=False, allow_blank=True)
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    def validate_email(self, value):
        value = value.strip().lower()
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Ya existe un usuario con ese correo electrónico.")
        return value

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError({"password_confirm": "Las contraseñas no coinciden."})
        validate_password(attrs["password"])
        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password")
        validated_data.pop("password_confirm")
        nombres = validated_data["nombres"].strip()
        apellidos = validated_data["apellidos"].strip()
        email = validated_data["email"]
        base_username = re.sub(r"[^a-z0-9]+", ".", email.split("@", 1)[0].lower()).strip(".") or "habitante"
        username = f"{base_username}.{uuid.uuid4().hex[:8]}"

        user = User.objects.create_user(
            username=username,
            email=email,
            first_name=nombres,
            last_name=apellidos,
            password=password,
        )
        Perfil.objects.create(
            usuario=user,
            nombres=nombres,
            apellidos=apellidos,
            telefono=validated_data.get("telefono", ""),
            numero_casa=validated_data.get("numero_casa", ""),
            codigo_postal=validated_data.get("codigo_postal", ""),
        )
        return user


class AdminUsuarioSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    role = serializers.SerializerMethodField()

    class Meta:
        model = Usuario
        fields = ("id", "username", "email", "first_name", "last_name", "password", "password_confirm", "is_active", "date_joined", "role")
        read_only_fields = ("id", "date_joined", "role")

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError({"password_confirm": "Las contraseñas no coinciden."})
        validate_password(attrs["password"])
        return attrs

    def get_role(self, obj):
        return "admin"

    def create(self, validated_data):
        password = validated_data.pop("password")
        validated_data.pop("password_confirm")
        user = Usuario(**validated_data, is_staff=True, is_superuser=True)
        user.set_password(password)
        user.save()
        return user


class CambiarPasswordSerializer(serializers.Serializer):
    password_actual = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = self.context["request"].user
        if not user.check_password(attrs["password_actual"]):
            raise serializers.ValidationError({"password_actual": "La contraseña actual no es correcta."})
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError({"password_confirm": "Las contraseñas no coinciden."})
        validate_password(attrs["password"], user=user)
        return attrs
