import uuid

from rest_framework import serializers

from common.choices import EstadoIntentoPago
from .models import Cuota, Pago, PagoIntento


class CuotaSerializer(serializers.ModelSerializer):
    mes = serializers.SerializerMethodField()

    class Meta:
        model = Cuota
        fields = ("id", "privada", "clave", "cuenta", "categoria", "descripcion", "nombre", "monto", "fecha_vencimiento", "tipo_pago", "icono", "color_icono", "mes", "status", "created_at")
        read_only_fields = ("id", "status", "created_at", "mes")
        extra_kwargs = {"clave": {"required": False}}

    def get_mes(self, obj):
        return obj.fecha_vencimiento.strftime("%B")

    def validate(self, attrs):
        if not attrs.get("clave"):
            privada = attrs.get("privada")
            fecha = attrs.get("fecha_vencimiento")
            nombre = attrs.get("nombre", "cuota")
            attrs["clave"] = f"{str(privada.id)[:8]}-{fecha:%Y%m%d}-{nombre[:18]}-{uuid.uuid4().hex[:6]}".lower().replace(" ", "-")
        return attrs


class PagoIntentoSerializer(serializers.ModelSerializer):
    validador_nombre = serializers.CharField(source="validador.nombre_completo", read_only=True)

    class Meta:
        model = PagoIntento
        fields = ("id", "comprobante_url", "estado", "enviado_en", "revisado_en", "validador", "validador_nombre", "motivo_declinado")
        read_only_fields = fields


class PagoSerializer(serializers.ModelSerializer):
    cuota_detalle = CuotaSerializer(source="cuota", read_only=True)
    pagador_detalle = serializers.SerializerMethodField()
    intentos = PagoIntentoSerializer(many=True, read_only=True)

    class Meta:
        model = Pago
        fields = ("id", "cuota", "cuota_detalle", "pagador", "pagador_detalle", "privada", "estado", "comprobante_url", "fecha_pago", "fecha_validacion", "validador", "intentos")
        read_only_fields = fields

    def get_pagador_detalle(self, obj):
        perfil = getattr(obj.pagador, "perfil", None)
        return {
            "id": str(obj.pagador_id),
            "nombre_completo": obj.pagador.nombre_completo,
            "email": obj.pagador.email,
            "telefono": getattr(perfil, "telefono", "") if perfil else "",
        }


class SubirComprobanteSerializer(serializers.Serializer):
    comprobante = serializers.ImageField()


class ValidarPagoSerializer(serializers.Serializer):
    estado = serializers.ChoiceField(choices=(EstadoIntentoPago.ACEPTADO, EstadoIntentoPago.DECLINADO))
    motivo = serializers.CharField(required=False, allow_blank=True, max_length=500)

    def validate(self, attrs):
        if attrs["estado"] == EstadoIntentoPago.DECLINADO and not attrs.get("motivo", "").strip():
            raise serializers.ValidationError({"motivo": "Indica por qué se declinó el comprobante."})
        return attrs
