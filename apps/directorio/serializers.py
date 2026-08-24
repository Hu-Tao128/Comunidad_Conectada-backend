from rest_framework import serializers

from common.gallery import sincronizar_galeria

from .models import Directorio, DirectorioImagen


class DirectorioGaleriaSerializer(serializers.ModelSerializer):
    url = serializers.ImageField(source="imagen", read_only=True)

    class Meta:
        model = DirectorioImagen
        fields = ("id", "url")


class DirectorioSerializer(serializers.ModelSerializer):
    galeria = DirectorioGaleriaSerializer(many=True, read_only=True)
    galeria_archivos = serializers.ListField(child=serializers.ImageField(), write_only=True, required=False)
    galeria_eliminar = serializers.ListField(child=serializers.UUIDField(), write_only=True, required=False)

    class Meta:
        model = Directorio
        fields = (
            "id", "privada", "nombre", "categorias", "num_tel", "codigo", "descripcion",
            "ubicacion", "tipo_ubicacion", "numero_casa", "direccion_externa", "maps_url",
            "imagenes", "galeria", "galeria_archivos", "galeria_eliminar", "status",
        )
        read_only_fields = ("id", "status")

    def validate(self, attrs):
        tipo_ubicacion = attrs.get("tipo_ubicacion", getattr(self.instance, "tipo_ubicacion", "local"))
        numero_casa = str(attrs.get("numero_casa", getattr(self.instance, "numero_casa", ""))).strip()
        direccion_externa = str(attrs.get("direccion_externa", getattr(self.instance, "direccion_externa", ""))).strip()
        if tipo_ubicacion == "local" and not numero_casa:
            raise serializers.ValidationError({"numero_casa": "Indica el número de casa dentro de la privada."})
        if tipo_ubicacion == "externo" and not direccion_externa:
            raise serializers.ValidationError({"direccion_externa": "Indica la dirección externa del servicio."})
        attrs["ubicacion"] = f"Dentro de la privada · Casa {numero_casa}" if tipo_ubicacion == "local" else direccion_externa
        return attrs

    def create(self, validated_data):
        gallery_files = validated_data.pop("galeria_archivos", [])
        validated_data.pop("galeria_eliminar", [])
        directorio = super().create(validated_data)
        sincronizar_galeria(
            directorio,
            related_name="galeria",
            model=DirectorioImagen,
            parent_field="directorio",
            files=gallery_files,
            removed_ids=[],
            user=self.context["request"].user,
        )
        return directorio

    def update(self, instance, validated_data):
        gallery_files = validated_data.pop("galeria_archivos", [])
        removed_ids = validated_data.pop("galeria_eliminar", [])
        directorio = super().update(instance, validated_data)
        sincronizar_galeria(
            directorio,
            related_name="galeria",
            model=DirectorioImagen,
            parent_field="directorio",
            files=gallery_files,
            removed_ids=removed_ids,
            user=self.context["request"].user,
        )
        return directorio
