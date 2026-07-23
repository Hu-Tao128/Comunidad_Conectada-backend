from rest_framework import serializers
from .models import Casa, Modulo, ModuloSistema, Privada, PrivadaMiembro, PrivadaModulo


class PrivadaSerializer(serializers.ModelSerializer):
    modulos = serializers.SerializerMethodField()
    modulos_contratados = serializers.SerializerMethodField()

    class Meta:
        model = Privada
        fields = ("id", "codigo", "nombre", "modulos", "modulos_contratados", "dir_num_exterior", "dir_colonia", "dir_calle", "dir_cp", "dir_ciudad", "dir_estado", "creador", "status")
        read_only_fields = ("id", "codigo", "creador", "status")

    def get_modulos(self, obj):
        return [
            {"id": str(modulo.id), "nombre": modulo.nombre}
            for modulo in obj.modulos.filter(status="activo", deleted_at__isnull=True)
        ]

    def get_modulos_contratados(self, obj):
        return [
            {"codigo": relacion.modulo.codigo, "nombre": relacion.modulo.nombre}
            for relacion in obj.modulos_contratados.filter(
                status="activo", deleted_at__isnull=True, modulo__activo=True
            ).select_related("modulo")
        ]


class PrivadaMiembroSerializer(serializers.ModelSerializer):
    privada_nombre = serializers.CharField(source="privada.nombre", read_only=True)
    privada_codigo = serializers.CharField(source="privada.codigo", read_only=True)
    modulos_contratados = serializers.SerializerMethodField()

    class Meta:
        model = PrivadaMiembro
        fields = ("id", "privada", "privada_nombre", "privada_codigo", "modulos_contratados", "usuario", "rol", "status")
        read_only_fields = ("id", "usuario", "rol", "status")

    def get_modulos_contratados(self, obj):
        return [
            relacion.modulo.codigo
            for relacion in obj.privada.modulos_contratados.filter(
                status="activo", deleted_at__isnull=True, modulo__activo=True
            ).select_related("modulo")
        ]


class ModuloSistemaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModuloSistema
        fields = ("id", "codigo", "nombre", "descripcion", "activo", "orden")
        read_only_fields = ("id",)


class PrivadaAdminSerializer(serializers.ModelSerializer):
    modulos_contratados = serializers.SerializerMethodField()
    habitantes = serializers.SerializerMethodField()

    class Meta:
        model = Privada
        fields = ("id", "codigo", "nombre", "creador", "habitantes", "modulos_contratados", "status", "created_at")

    def get_habitantes(self, obj):
        return obj.miembros.filter(status="activo", deleted_at__isnull=True).count()

    def get_modulos_contratados(self, obj):
        return list(obj.modulos_contratados.filter(status="activo", deleted_at__isnull=True).values_list("modulo__codigo", flat=True))


class AdminPrivadaModulosSerializer(serializers.Serializer):
    modulos_contratados = serializers.ListField(
        child=serializers.SlugField(max_length=60),
        allow_empty=True,
    )

    def validate_modulos_contratados(self, value):
        codes = set(value)
        available = set(ModuloSistema.objects.filter(codigo__in=codes, activo=True).values_list("codigo", flat=True))
        missing = sorted(codes - available)
        if missing:
            raise serializers.ValidationError({"no_disponibles": missing})
        return list(codes)


class CrearPrivadaSerializer(serializers.ModelSerializer):
    modulos = serializers.ListField(
        child=serializers.CharField(max_length=100),
        required=False,
        allow_empty=True,
        write_only=True,
    )
    modulos_contratados = serializers.ListField(
        child=serializers.SlugField(max_length=60),
        required=False,
        allow_empty=True,
        write_only=True,
    )

    class Meta:
        model = Privada
        fields = ("nombre", "modulos", "modulos_contratados", "dir_num_exterior", "dir_colonia", "dir_calle", "dir_cp", "dir_ciudad", "dir_estado")

    def validate_modulos(self, value):
        cleaned = [nombre.strip() for nombre in value if nombre.strip()]
        if len({nombre.casefold() for nombre in cleaned}) != len(cleaned):
            raise serializers.ValidationError("No puede haber módulos repetidos.")
        return cleaned

    def validate_modulos_contratados(self, value):
        cleaned = list(dict.fromkeys(value))
        existentes = set(ModuloSistema.objects.filter(codigo__in=cleaned, activo=True).values_list("codigo", flat=True))
        faltantes = sorted(set(cleaned) - existentes)
        if faltantes:
            raise serializers.ValidationError({"no_disponibles": faltantes})
        return cleaned


class UnirsePrivadaSerializer(serializers.Serializer):
    codigo = serializers.CharField(max_length=30)

    def validate_codigo(self, value):
        return value.strip().upper()


class ModuloSerializer(serializers.ModelSerializer):
    class Meta:
        model = Modulo
        fields = ("id", "privada", "nombre", "status")


class CasaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Casa
        fields = ("id", "modulo", "numero", "status")
