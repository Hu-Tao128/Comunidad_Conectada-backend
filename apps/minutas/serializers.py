from rest_framework import serializers

from .models import Minuta


class MinutaSerializer(serializers.ModelSerializer):
    moderador_detalle = serializers.SerializerMethodField()
    asistentes_lista = serializers.SerializerMethodField()

    class Meta:
        model = Minuta
        fields = (
            "id", "privada", "numero", "titulo", "tipo_reunion", "fecha_reunion", "lugar",
            "objetivo", "asistentes", "asistentes_lista", "orden_dia", "acuerdos",
            "compromisos", "observaciones", "proxima_reunion", "moderador",
            "moderador_detalle", "created_at", "updated_at",
        )
        read_only_fields = ("id", "numero", "moderador", "moderador_detalle", "created_at", "updated_at")

    def get_asistentes_lista(self, obj):
        return [linea.strip() for linea in obj.asistentes.splitlines() if linea.strip()]

    def get_moderador_detalle(self, obj):
        perfil = getattr(obj.moderador, "perfil", None)
        nombre = f"{getattr(perfil, 'nombres', '') or obj.moderador.first_name} {getattr(perfil, 'apellidos', '') or obj.moderador.last_name}".strip()
        return {"id": str(obj.moderador_id), "nombre": nombre or obj.moderador.username,
                "email": obj.moderador.email, "telefono": getattr(perfil, "telefono", "")}
