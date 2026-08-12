from rest_framework import serializers

from apps.galeria.serializers import GaleriaSerializerMixin

from .models import Directorio


class DirectorioSerializer(GaleriaSerializerMixin, serializers.ModelSerializer):
    GALERIA_FK = "directorio"

    galeria = serializers.SerializerMethodField()
    galeria_archivos = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False,
    )
    galeria_eliminar = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False,
    )

    class Meta:
        model = Directorio
        fields = (
            "id",
            "privada",
            "nombre",
            "categorias",
            "num_tel",
            "codigo",
            "descripcion",
            "ubicacion",
            "imagenes",
            "galeria",
            "galeria_archivos",
            "galeria_eliminar",
            "status",
        )
        read_only_fields = ("id", "status")
