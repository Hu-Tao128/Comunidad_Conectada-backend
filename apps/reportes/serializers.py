from django.conf import settings
import cloudinary
import cloudinary.uploader
from rest_framework import serializers

from common.gallery import validar_imagen

from .models import Incidente, IncidenteImagen, Reporte, ReporteImagen, TipoReporte


def subir_evidencia(archivo, *, usuario_id, privada_id) -> str:
    validar_imagen(archivo, "evidencia_archivo")
    if not all((settings.CLOUDINARY_CLOUD_NAME, settings.CLOUDINARY_API_KEY, settings.CLOUDINARY_API_SECRET)):
        raise serializers.ValidationError({"evidencia_archivo": "Cloudinary no está configurado en el servidor."})
    cloudinary.config(cloud_name=settings.CLOUDINARY_CLOUD_NAME, api_key=settings.CLOUDINARY_API_KEY,
                      api_secret=settings.CLOUDINARY_API_SECRET, secure=True)
    resultado = cloudinary.uploader.upload(
        archivo, folder=f"comunidad_conectada/incidentes/{privada_id}/{usuario_id}",
        resource_type="image", overwrite=False,
    )
    return resultado["secure_url"]


class ReporteGaleriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReporteImagen
        fields = ("id", "url")


class IncidenteGaleriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = IncidenteImagen
        fields = ("id", "url")


class TipoReporteSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoReporte
        fields = ("id", "codigo", "nombre")


class IncidenteSerializer(serializers.ModelSerializer):
    evidencia_archivo = serializers.ImageField(write_only=True, required=False)
    galeria = IncidenteGaleriaSerializer(many=True, read_only=True)
    galeria_archivos = serializers.ListField(child=serializers.ImageField(), write_only=True, required=False)
    galeria_eliminar = serializers.ListField(child=serializers.UUIDField(), write_only=True, required=False)
    fecha_incidente = serializers.DateTimeField(required=True, allow_null=False)
    tipo_detalle = TipoReporteSerializer(source="tipo_categoria", read_only=True)
    habitante = serializers.SerializerMethodField()
    tiene_reporte = serializers.SerializerMethodField()
    reporte_id = serializers.SerializerMethodField()

    class Meta:
        model = Incidente
        fields = (
            "id", "num", "titulo", "descripcion", "tipo_categoria", "tipo_detalle",
            "prioridad", "estado", "fecha_incidente", "fecha_registro", "ubicacion",
            "evidencia", "evidencia_archivo", "galeria", "galeria_archivos", "galeria_eliminar",
            "usuario", "habitante", "privada",
            "tiene_reporte", "reporte_id", "created_at",
        )
        read_only_fields = ("id", "num", "evidencia", "usuario", "habitante", "estado", "fecha_registro", "tiene_reporte", "reporte_id", "created_at")

    def get_habitante(self, obj):
        perfil = getattr(obj.usuario, "perfil", None)
        nombre = f"{getattr(perfil, 'nombres', '') or obj.usuario.first_name} {getattr(perfil, 'apellidos', '') or obj.usuario.last_name}".strip()
        return {"id": str(obj.usuario_id), "nombre": nombre or obj.usuario.username,
                "email": obj.usuario.email, "telefono": getattr(perfil, "telefono", "")}

    def get_tiene_reporte(self, obj):
        return obj.reportes_seguimiento.filter(status="activo", deleted_at__isnull=True).exists()

    def get_reporte_id(self, obj):
        reporte = obj.reportes_seguimiento.filter(status="activo", deleted_at__isnull=True).order_by("-created_at").first()
        return str(reporte.id) if reporte else None

    def create(self, validated_data):
        archivo = validated_data.pop("evidencia_archivo", None)
        gallery_files = validated_data.pop("galeria_archivos", [])
        validated_data.pop("galeria_eliminar", [])
        incidente = super().create(validated_data)
        if archivo:
            incidente.evidencia = subir_evidencia(archivo, usuario_id=incidente.usuario_id, privada_id=incidente.privada_id)
            incidente.save(update_fields=("evidencia", "updated_at"))
        for image in gallery_files:
            IncidenteImagen.objects.create(
                incidente=incidente,
                url=subir_evidencia(image, usuario_id=incidente.usuario_id, privada_id=incidente.privada_id),
                created_by=self.context["request"].user,
                updated_by=self.context["request"].user,
            )
        return incidente

    def update(self, instance, validated_data):
        archivo = validated_data.pop("evidencia_archivo", None)
        gallery_files = validated_data.pop("galeria_archivos", [])
        removed_ids = validated_data.pop("galeria_eliminar", [])
        incidente = super().update(instance, validated_data)
        if archivo:
            incidente.evidencia = subir_evidencia(archivo, usuario_id=incidente.usuario_id, privada_id=incidente.privada_id)
            incidente.save(update_fields=("evidencia", "updated_at"))
        if removed_ids:
            incidente.galeria.filter(id__in=removed_ids).delete()
        for image in gallery_files:
            IncidenteImagen.objects.create(
                incidente=incidente,
                url=subir_evidencia(image, usuario_id=incidente.usuario_id, privada_id=incidente.privada_id),
                created_by=self.context["request"].user,
                updated_by=self.context["request"].user,
            )
        return incidente


class ReporteSerializer(serializers.ModelSerializer):
    evidencia_archivo = serializers.ImageField(write_only=True, required=False)
    galeria = ReporteGaleriaSerializer(many=True, read_only=True)
    galeria_archivos = serializers.ListField(child=serializers.ImageField(), write_only=True, required=False)
    galeria_eliminar = serializers.ListField(child=serializers.UUIDField(), write_only=True, required=False)
    incidente_detalle = IncidenteSerializer(source="incidente", read_only=True)
    tipo_detalle = TipoReporteSerializer(source="tipo_categoria", read_only=True)
    moderador = serializers.SerializerMethodField()

    class Meta:
        model = Reporte
        fields = (
            "id", "num", "privada", "incidente", "incidente_detalle", "creador", "moderador",
            "titulo", "descripcion", "tipo_categoria", "tipo_detalle", "prioridad", "estado",
            "fecha_suceso", "evidencia", "evidencia_archivo", "galeria", "galeria_archivos",
            "galeria_eliminar", "created_at", "updated_at",
        )
        read_only_fields = ("id", "num", "privada", "creador", "moderador", "estado", "tipo_categoria", "tipo_detalle", "prioridad", "fecha_suceso", "evidencia", "created_at", "updated_at")

    def get_moderador(self, obj):
        perfil = getattr(obj.creador, "perfil", None)
        nombre = f"{getattr(perfil, 'nombres', '') or obj.creador.first_name} {getattr(perfil, 'apellidos', '') or obj.creador.last_name}".strip()
        return {"id": str(obj.creador_id), "nombre": nombre or obj.creador.username,
                "telefono": getattr(perfil, "telefono", ""), "email": obj.creador.email}

    def validate_incidente(self, incidente):
        if self.instance:
            return incidente
        return incidente

    def validate(self, attrs):
        if not self.instance and not attrs.get("evidencia_archivo"):
            raise serializers.ValidationError({"evidencia_archivo": "Adjunta una evidencia fotográfica."})
        return attrs

    def create(self, validated_data):
        archivo = validated_data.pop("evidencia_archivo", None)
        gallery_files = validated_data.pop("galeria_archivos", [])
        validated_data.pop("galeria_eliminar", [])
        reporte = super().create(validated_data)
        if archivo:
            reporte.evidencia = subir_evidencia(archivo, usuario_id=reporte.creador_id, privada_id=reporte.privada_id)
            reporte.save(update_fields=("evidencia", "updated_at"))
        for image in gallery_files:
            ReporteImagen.objects.create(
                reporte=reporte,
                url=subir_evidencia(image, usuario_id=reporte.creador_id, privada_id=reporte.privada_id),
                created_by=self.context["request"].user,
                updated_by=self.context["request"].user,
            )
        return reporte

    def update(self, instance, validated_data):
        archivo = validated_data.pop("evidencia_archivo", None)
        gallery_files = validated_data.pop("galeria_archivos", [])
        removed_ids = validated_data.pop("galeria_eliminar", [])
        reporte = super().update(instance, validated_data)
        if archivo:
            reporte.evidencia = subir_evidencia(archivo, usuario_id=reporte.creador_id, privada_id=reporte.privada_id)
            reporte.save(update_fields=("evidencia", "updated_at"))
        if removed_ids:
            reporte.galeria.filter(id__in=removed_ids).delete()
        for image in gallery_files:
            ReporteImagen.objects.create(
                reporte=reporte,
                url=subir_evidencia(image, usuario_id=reporte.creador_id, privada_id=reporte.privada_id),
                created_by=self.context["request"].user,
                updated_by=self.context["request"].user,
            )
        return reporte
