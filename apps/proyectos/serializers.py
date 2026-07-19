from rest_framework import serializers
from .models import Proyecto


class ProyectoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proyecto
        fields = ("id", "codigo", "privada", "nombre", "descripcion", "capacidad", "tipo", "estado", "fecha_inicio", "fecha_fin", "usuario")
