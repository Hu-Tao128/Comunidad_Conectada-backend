from rest_framework import serializers

from apps.galeria.serializers import GaleriaSerializerMixin

from .models import Evento


class EventoSerializer(GaleriaSerializerMixin, serializers.ModelSerializer):
    GALERIA_FK = "evento"

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
        model = Evento
        fields = (
            "id",
            "privada",
            "titulo",
            "descripcion",
            "fecha_inicio",
            "fecha_fin",
            "ubicacion",
            "capacidad",
            "imagen",
            "galeria",
            "galeria_archivos",
            "galeria_eliminar",
            "status",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "status", "created_at", "updated_at")

    def validate(self, attrs):
        fecha_inicio = attrs.get(
            "fecha_inicio", getattr(self.instance, "fecha_inicio", None)
        )
        fecha_fin = attrs.get("fecha_fin", getattr(self.instance, "fecha_fin", None))
        if fecha_inicio and fecha_fin and fecha_fin < fecha_inicio:
            raise serializers.ValidationError(
                {"fecha_fin": "La fecha final debe ser posterior a la inicial."}
            )
        return attrs
