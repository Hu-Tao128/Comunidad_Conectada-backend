from rest_framework import serializers
from .models import Reservacion


class ReservacionSerializer(serializers.ModelSerializer):
    area_nombre = serializers.CharField(source="area.nombre", read_only=True)
    usuario_nombre = serializers.CharField(
        source="usuario.nombre_completo", read_only=True
    )

    class Meta:
        model = Reservacion
        fields = (
            "id",
            "folio",
            "area",
            "area_nombre",
            "usuario",
            "usuario_nombre",
            "fecha",
            "hora_inicio",
            "hora_fin",
            "num_asistentes",
            "estado",
            "descripcion",
        )
        read_only_fields = ("id", "folio", "usuario", "usuario_nombre", "estado")

    def validate_area(self, area):
        request = self.context.get("request")
        if request and not request.user.is_staff:
            from apps.communities.models import PrivadaMiembro

            if not PrivadaMiembro.objects.filter(
                privada=area.privada,
                usuario=request.user,
                status="activo",
                deleted_at__isnull=True,
            ).exists():
                raise serializers.ValidationError(
                    "No perteneces a la privada de esta área."
                )
        return area

    def validate(self, attrs):
        area = attrs.get("area", getattr(self.instance, "area", None))
        fecha = attrs.get("fecha", getattr(self.instance, "fecha", None))
        hora_inicio = attrs.get(
            "hora_inicio", getattr(self.instance, "hora_inicio", None)
        )
        hora_fin = attrs.get("hora_fin", getattr(self.instance, "hora_fin", None))

        if hora_inicio and hora_fin and hora_fin <= hora_inicio:
            raise serializers.ValidationError(
                {"hora_fin": "La hora final debe ser posterior a la inicial."}
            )

        if area and fecha and hora_inicio and hora_fin:
            cruces = Reservacion.objects.filter(
                area=area,
                fecha=fecha,
                status="activo",
                deleted_at__isnull=True,
                hora_inicio__lt=hora_fin,
                hora_fin__gt=hora_inicio,
            ).exclude(estado="cancelada")
            if self.instance:
                cruces = cruces.exclude(pk=self.instance.pk)
            if cruces.exists():
                raise serializers.ValidationError(
                    "El área ya está reservada en ese horario."
                )

        return attrs
