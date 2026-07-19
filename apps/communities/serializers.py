from rest_framework import serializers
from .models import Casa, Modulo, Privada


class PrivadaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Privada
        fields = ("id", "codigo", "nombre", "dir_num_exterior", "dir_colonia", "dir_calle", "dir_cp", "dir_ciudad", "dir_estado", "creador", "status")


class ModuloSerializer(serializers.ModelSerializer):
    class Meta:
        model = Modulo
        fields = ("id", "privada", "nombre", "status")


class CasaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Casa
        fields = ("id", "modulo", "numero", "status")
