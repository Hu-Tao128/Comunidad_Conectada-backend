from rest_framework import serializers
from .models import Reservacion


class ReservacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservacion
        fields = ("id", "folio", "area", "usuario", "fecha", "hora_inicio", "hora_fin", "num_asistentes", "estado", "descripcion")
