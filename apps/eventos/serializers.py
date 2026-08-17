from rest_framework import serializers

from .models import Evento


class EventoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evento
        fields = (
            "id", "privada", "titulo", "descripcion", "fecha_inicio", "fecha_fin",
            "ubicacion", "capacidad", "imagen", "status", "created_at", "updated_at",
        )
        read_only_fields = ("id", "status", "created_at", "updated_at")

    def validate(self, attrs):
        fecha_inicio = attrs.get("fecha_inicio", getattr(self.instance, "fecha_inicio", None))
        fecha_fin = attrs.get("fecha_fin", getattr(self.instance, "fecha_fin", None))
        if fecha_inicio and fecha_fin and fecha_fin < fecha_inicio:
            raise serializers.ValidationError({"fecha_fin": "La fecha final debe ser posterior a la inicial."})
        return attrs
