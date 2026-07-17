from rest_framework import serializers
from .models import AreaComunitaria


class AreaComunitariaSerializer(serializers.ModelSerializer):
    class Meta:
        model = AreaComunitaria
        fields = ("id", "privada", "codigo", "nombre", "descripcion", "imagen", "capacidad", "status")
