from rest_framework import serializers

from apps.communities.models import PrivadaMiembro, RolPrivada
from .models import EntregaObjeto, EvidenciaPropiedad, ObjetoPerdido, PreguntaValidacion, Reclamacion, RespuestaValidacion


class UsuarioResumenSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    nombre = serializers.CharField(source="nombre_completo")
    telefono = serializers.SerializerMethodField()

    def get_telefono(self, usuario):
        perfil = getattr(usuario, "perfil", None)
        return getattr(perfil, "telefono", "") or ""


class PreguntaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PreguntaValidacion
        fields = ("id", "pregunta", "orden")
        read_only_fields = ("id",)


class ObjetoPerdidoSerializer(serializers.ModelSerializer):
    reportado_por_detalle = UsuarioResumenSerializer(source="reportado_por", read_only=True)
    responsable_resguardo_detalle = UsuarioResumenSerializer(source="responsable_resguardo", read_only=True)
    posible_localizador_detalle = UsuarioResumenSerializer(source="posible_localizador", read_only=True)
    preguntas = PreguntaSerializer(source="preguntas_validacion", many=True, required=False)
    preguntas_json = serializers.JSONField(write_only=True, required=False)
    finalizado = serializers.BooleanField(read_only=True)
    mi_reclamacion = serializers.SerializerMethodField()

    class Meta:
        model = ObjetoPerdido
        fields = ("id", "num", "privada", "reportado_por", "reportado_por_detalle", "nombre", "descripcion", "tipo", "estado_caso", "finalizado", "imagen", "ubicacion", "fecha_evento", "informacion_adicional", "detalles_privados", "responsable_resguardo", "responsable_resguardo_detalle", "posible_localizador", "posible_localizador_detalle", "fecha_reporte", "fecha_encontrado", "fecha_devuelto", "recuperador", "preguntas", "preguntas_json", "mi_reclamacion", "status", "created_at", "updated_at")
        read_only_fields = ("id", "num", "reportado_por", "estado_caso", "posible_localizador", "fecha_reporte", "fecha_encontrado", "fecha_devuelto", "recuperador", "status", "created_at", "updated_at")

    def get_mi_reclamacion(self, instance):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return None
        reclamacion = instance.reclamaciones.filter(
            solicitante=user, status="activo", deleted_at__isnull=True,
        ).prefetch_related("respuestas__pregunta").first()
        if not reclamacion:
            return None
        return {
            "id": str(reclamacion.id),
            "estado": reclamacion.estado,
            "estado_display": reclamacion.get_estado_display(),
            "mensaje": reclamacion.mensaje,
            "notas_revision": reclamacion.notas_revision,
            "created_at": reclamacion.created_at,
            "respuestas": [
                {
                    "pregunta": respuesta.pregunta.pregunta,
                    "respuesta": respuesta.respuesta,
                }
                for respuesta in reclamacion.respuestas.all()
            ],
        }

    def validate(self, attrs):
        preguntas_json = attrs.pop("preguntas_json", None)
        if preguntas_json is not None:
            if not isinstance(preguntas_json, list):
                raise serializers.ValidationError({"preguntas_json": "Debe ser una lista."})
            attrs["preguntas_validacion"] = [{"pregunta": str(texto).strip(), "orden": index} for index, texto in enumerate(preguntas_json, 1) if str(texto).strip()]
        tipo = attrs.get("tipo", getattr(self.instance, "tipo", None))
        if self.instance and tipo != self.instance.tipo:
            raise serializers.ValidationError({"tipo": "El tipo de publicación no puede cambiarse después de crearla."})
        preguntas = attrs.get("preguntas_validacion", [])
        if tipo == ObjetoPerdido.Tipo.RESGUARDADO:
            if self.instance is None and not (1 <= len(preguntas) <= 5):
                raise serializers.ValidationError({"preguntas": "Registra entre una y cinco preguntas privadas."})
        elif preguntas:
            raise serializers.ValidationError({"preguntas": "Las preguntas solo aplican a objetos resguardados."})
        return attrs

    def create(self, validated_data):
        preguntas = validated_data.pop("preguntas_validacion", [])
        objeto = super().create(validated_data)
        for index, pregunta in enumerate(preguntas, 1):
            PreguntaValidacion.objects.create(objeto=objeto, orden=pregunta.get("orden", index), pregunta=pregunta["pregunta"], created_by=objeto.reportado_por)
        return objeto

    def update(self, instance, validated_data):
        preguntas = validated_data.pop("preguntas_validacion", None)
        objeto = super().update(instance, validated_data)
        if preguntas is not None and not instance.reclamaciones.exists():
            instance.preguntas_validacion.all().delete()
            for index, pregunta in enumerate(preguntas, 1):
                PreguntaValidacion.objects.create(objeto=objeto, orden=pregunta.get("orden", index), pregunta=pregunta["pregunta"], created_by=self.context["request"].user)
        return objeto

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get("request")
        user = getattr(request, "user", None)
        es_moderador = user and PrivadaMiembro.objects.filter(
            privada_id=instance.privada_id, usuario=user, rol=RolPrivada.MODERADOR,
            status="activo", deleted_at__isnull=True,
        ).exists()
        sensible = user and (user.is_staff or es_moderador or user.id in {instance.reportado_por_id, instance.responsable_resguardo_id})
        if instance.tipo == ObjetoPerdido.Tipo.RESGUARDADO and not sensible:
            data.pop("detalles_privados", None)
            data.pop("preguntas", None)
        return data


class RespuestaSerializer(serializers.ModelSerializer):
    pregunta_texto = serializers.CharField(source="pregunta.pregunta", read_only=True)
    class Meta:
        model = RespuestaValidacion
        fields = ("id", "pregunta", "pregunta_texto", "respuesta")
        read_only_fields = ("id",)


class EvidenciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = EvidenciaPropiedad
        fields = ("id", "archivo", "descripcion")
        read_only_fields = ("id",)


class ReclamacionSerializer(serializers.ModelSerializer):
    respuestas = RespuestaSerializer(many=True)
    evidencias = EvidenciaSerializer(many=True, required=False)
    solicitante_detalle = UsuarioResumenSerializer(source="solicitante", read_only=True)

    class Meta:
        model = Reclamacion
        fields = ("id", "objeto", "solicitante", "solicitante_detalle", "estado", "mensaje", "notas_revision", "revisada_por", "revisada_en", "respuestas", "evidencias", "created_at")
        read_only_fields = ("id", "solicitante", "estado", "notas_revision", "revisada_por", "revisada_en", "created_at")

    def validate(self, attrs):
        objeto = attrs["objeto"]
        request = self.context.get("request")
        if request and Reclamacion.objects.filter(
            objeto=objeto,
            solicitante=request.user,
            status="activo",
            deleted_at__isnull=True,
        ).exists():
            raise serializers.ValidationError({
                "objeto": "Ya enviaste una reclamación para este objeto. Está disponible en el seguimiento de tus solicitudes."
            })
        if objeto.tipo != ObjetoPerdido.Tipo.RESGUARDADO or objeto.finalizado:
            raise serializers.ValidationError("Este objeto no admite reclamaciones.")
        preguntas = {p.id for p in objeto.preguntas_validacion.all()}
        respondidas = {r["pregunta"].id for r in attrs.get("respuestas", [])}
        if preguntas != respondidas:
            raise serializers.ValidationError({"respuestas": "Debes responder todas las preguntas privadas."})
        return attrs

    def create(self, validated_data):
        respuestas = validated_data.pop("respuestas")
        evidencias = validated_data.pop("evidencias", [])
        reclamacion = Reclamacion.objects.create(**validated_data)
        for respuesta in respuestas:
            RespuestaValidacion.objects.create(reclamacion=reclamacion, **respuesta, created_by=reclamacion.solicitante)
        for evidencia in evidencias:
            EvidenciaPropiedad.objects.create(reclamacion=reclamacion, **evidencia, created_by=reclamacion.solicitante)
        return reclamacion


class EntregaSerializer(serializers.ModelSerializer):
    confirmada = serializers.BooleanField(read_only=True)
    class Meta:
        model = EntregaObjeto
        fields = ("id", "objeto", "reclamacion", "entregado_por", "recibido_por", "autorizado_por", "resultado", "fecha_entrega", "confirmacion_entrega", "confirmacion_recepcion", "codigo_temporal", "codigo_expira_en", "codigo_usado_en", "confirmada")
        read_only_fields = ("id", "autorizado_por", "confirmacion_entrega", "confirmacion_recepcion", "codigo_temporal", "codigo_expira_en", "codigo_usado_en")

    def validate(self, attrs):
        objeto = attrs.get("objeto")
        if objeto and EntregaObjeto.objects.filter(objeto=objeto, status="activo", deleted_at__isnull=True).exists():
            raise serializers.ValidationError({"objeto": "Este objeto ya tiene una entrega registrada."})
        if objeto and objeto.finalizado:
            raise serializers.ValidationError({"objeto": "El caso ya está finalizado."})
        if attrs.get("entregado_por") == attrs.get("recibido_por"):
            raise serializers.ValidationError("Quien entrega y quien recibe deben ser personas diferentes.")
        return attrs
