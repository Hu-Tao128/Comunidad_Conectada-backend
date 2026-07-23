from rest_framework import serializers
from .models import Incidente, Reporte


class ReporteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reporte
        fields = ("id", "num", "privada", "creador", "supervisor", "titulo", "descripcion", "tipo", "prioridad", "estado", "fecha_suceso", "hora_suceso", "evidencia", "status")
        read_only_fields = ("id", "num", "creador", "supervisor", "estado", "status")
        extra_kwargs = {"privada": {"required": False}}

    def validate_privada(self, privada):
        """Solo permite reportar en una privada a la que pertenece el usuario."""
        request = self.context.get("request")
        if request and not request.user.is_staff:
            from apps.communities.models import PrivadaMiembro

            es_miembro = PrivadaMiembro.objects.filter(
                privada=privada,
                usuario=request.user,
                status="activo",
                deleted_at__isnull=True,
            ).exists()
            if not es_miembro:
                raise serializers.ValidationError(
                    "No perteneces a la privada seleccionada."
                )
        return privada

    def validate(self, attrs):
        if not self.instance and "privada" not in attrs:
            raise serializers.ValidationError(
                {"privada": "Este campo es requerido."}
            )
        if self.instance and "privada" in attrs:
            raise serializers.ValidationError(
                {"privada": "No se puede cambiar la privada de un reporte."}
            )
        return attrs


class IncidenteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Incidente
        fields = ("id", "num", "reporte", "tipo", "prioridad", "estado", "fecha_incidente", "fecha_registro", "usuario", "privada", "ubicacion", "evidencia", "status")
