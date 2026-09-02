from rest_framework import serializers

from common.gallery import sincronizar_galeria

from .models import Evento, EventoImagen


class EventoGaleriaSerializer(serializers.ModelSerializer):
    url = serializers.ImageField(source="imagen", read_only=True)

    class Meta:
        model = EventoImagen
        fields = ("id", "url")


class EventoSerializer(serializers.ModelSerializer):
    galeria = EventoGaleriaSerializer(many=True, read_only=True)
    galeria_archivos = serializers.ListField(child=serializers.ImageField(), write_only=True, required=False)
    galeria_eliminar = serializers.ListField(child=serializers.UUIDField(), write_only=True, required=False)

    class Meta:
        model = Evento
        fields = (
            "id", "privada", "titulo", "descripcion", "fecha_inicio", "fecha_fin",
            "ubicacion", "capacidad", "imagen", "galeria", "galeria_archivos",
            "galeria_eliminar", "status", "created_at", "updated_at",
        )
        read_only_fields = ("id", "status", "created_at", "updated_at")

    def validate(self, attrs):
        fecha_inicio = attrs.get("fecha_inicio", getattr(self.instance, "fecha_inicio", None))
        fecha_fin = attrs.get("fecha_fin", getattr(self.instance, "fecha_fin", None))
        if fecha_inicio and fecha_fin and fecha_fin < fecha_inicio:
            raise serializers.ValidationError({"fecha_fin": "La fecha final debe ser posterior a la inicial."})
        return attrs

    def create(self, validated_data):
        gallery_files = validated_data.pop("galeria_archivos", [])
        validated_data.pop("galeria_eliminar", [])
        evento = super().create(validated_data)
        sincronizar_galeria(
            evento,
            related_name="galeria",
            model=EventoImagen,
            parent_field="evento",
            files=gallery_files,
            removed_ids=[],
            user=self.context["request"].user,
        )
        return evento

    def update(self, instance, validated_data):
        gallery_files = validated_data.pop("galeria_archivos", [])
        removed_ids = validated_data.pop("galeria_eliminar", [])
        evento = super().update(instance, validated_data)
        sincronizar_galeria(
            evento,
            related_name="galeria",
            model=EventoImagen,
            parent_field="evento",
            files=gallery_files,
            removed_ids=removed_ids,
            user=self.context["request"].user,
        )
        return evento
