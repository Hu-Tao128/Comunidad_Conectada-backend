from rest_framework import serializers

from common.gallery import sincronizar_galeria

from .models import Proyecto, ProyectoImagen


class ProyectoGaleriaSerializer(serializers.ModelSerializer):
    url = serializers.ImageField(source="imagen", read_only=True)

    class Meta:
        model = ProyectoImagen
        fields = ("id", "url")


class ProyectoSerializer(serializers.ModelSerializer):
    galeria = ProyectoGaleriaSerializer(many=True, read_only=True)
    galeria_archivos = serializers.ListField(child=serializers.ImageField(), write_only=True, required=False)
    galeria_eliminar = serializers.ListField(child=serializers.UUIDField(), write_only=True, required=False)

    class Meta:
        model = Proyecto
        fields = (
            "id", "codigo", "privada", "nombre", "descripcion", "capacidad", "tipo",
            "estado", "fecha_inicio", "fecha_fin", "imagen", "galeria", "galeria_archivos",
            "galeria_eliminar", "usuario",
        )

    def create(self, validated_data):
        gallery_files = validated_data.pop("galeria_archivos", [])
        validated_data.pop("galeria_eliminar", [])
        proyecto = super().create(validated_data)
        sincronizar_galeria(
            proyecto,
            related_name="galeria",
            model=ProyectoImagen,
            parent_field="proyecto",
            files=gallery_files,
            removed_ids=[],
            user=self.context["request"].user,
        )
        return proyecto

    def update(self, instance, validated_data):
        gallery_files = validated_data.pop("galeria_archivos", [])
        removed_ids = validated_data.pop("galeria_eliminar", [])
        proyecto = super().update(instance, validated_data)
        sincronizar_galeria(
            proyecto,
            related_name="galeria",
            model=ProyectoImagen,
            parent_field="proyecto",
            files=gallery_files,
            removed_ids=removed_ids,
            user=self.context["request"].user,
        )
        return proyecto
