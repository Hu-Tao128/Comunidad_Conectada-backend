from rest_framework import serializers
from .models import ObjetoPerdido


class ObjetoPerdidoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ObjetoPerdido
        fields = ("id", "num", "privada", "reportado_por", "nombre", "descripcion", "imagen", "tipo", "fecha_reporte", "fecha_encontrado", "fecha_devuelto", "recuperador", "status")
