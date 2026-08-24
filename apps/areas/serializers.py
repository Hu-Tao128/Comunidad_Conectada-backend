from rest_framework import serializers

from common.gallery import sincronizar_galeria

from .models import AreaComunitaria, AreaImagen


class AreaGaleriaSerializer(serializers.ModelSerializer):
    url = serializers.ImageField(source="imagen", read_only=True)

    class Meta:
        model = AreaImagen
        fields = ("id", "url")


class AreaComunitariaSerializer(serializers.ModelSerializer):
    galeria = AreaGaleriaSerializer(many=True, read_only=True)
    galeria_archivos = serializers.ListField(child=serializers.ImageField(), write_only=True, required=False)
    galeria_eliminar = serializers.ListField(child=serializers.UUIDField(), write_only=True, required=False)

    class Meta:
        model = AreaComunitaria
        fields = ("id", "privada", "codigo", "nombre", "descripcion", "imagen", "galeria", "galeria_archivos", "galeria_eliminar", "capacidad", "status")
        read_only_fields = ("id", "status")

    def create(self, validated_data):
        gallery_files = validated_data.pop("galeria_archivos", [])
        validated_data.pop("galeria_eliminar", [])
        area = super().create(validated_data)
        sincronizar_galeria(
            area,
            related_name="galeria",
            model=AreaImagen,
            parent_field="area",
            files=gallery_files,
            removed_ids=[],
            user=self.context["request"].user,
        )
        return area

    def update(self, instance, validated_data):
        gallery_files = validated_data.pop("galeria_archivos", [])
        removed_ids = validated_data.pop("galeria_eliminar", [])
        area = super().update(instance, validated_data)
        sincronizar_galeria(
            area,
            related_name="galeria",
            model=AreaImagen,
            parent_field="area",
            files=gallery_files,
            removed_ids=removed_ids,
            user=self.context["request"].user,
        )
        return area
