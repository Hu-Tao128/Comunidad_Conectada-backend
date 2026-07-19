from rest_framework import serializers

from .models import Directorio


class DirectorioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Directorio
        fields = ("id", "privada", "nombre", "categorias", "num_tel", "codigo", "descripcion", "ubicacion", "imagenes", "status")
