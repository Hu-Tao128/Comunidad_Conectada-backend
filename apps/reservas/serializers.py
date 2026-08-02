from rest_framework import serializers
from .models import Reservacion


class ReservacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservacion
        fields = ("id", "folio", "area", "usuario", "fecha", "hora_inicio", "hora_fin", "num_asistentes", "estado", "descripcion")
        read_only_fields = ("id", "folio", "usuario")

    def validate(self, attrs):
        hora_inicio = attrs.get("hora_inicio", getattr(self.instance, "hora_inicio", None))
        hora_fin = attrs.get("hora_fin", getattr(self.instance, "hora_fin", None))
        if hora_inicio and hora_fin and hora_fin <= hora_inicio:
            raise serializers.ValidationError({"hora_fin": "La hora final debe ser posterior a la inicial."})
        return attrs
