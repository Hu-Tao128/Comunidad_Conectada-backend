from rest_framework import serializers
from .models import Incidente, Reporte


class ReporteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reporte
        fields = ("id", "num", "privada", "creador", "supervisor", "titulo", "descripcion", "tipo", "prioridad", "estado", "fecha_suceso", "hora_suceso", "evidencia", "status")


class IncidenteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Incidente
        fields = ("id", "num", "reporte", "tipo", "prioridad", "estado", "fecha_incidente", "fecha_registro", "usuario", "privada", "ubicacion", "evidencia", "status")
