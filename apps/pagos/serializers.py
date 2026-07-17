from rest_framework import serializers
from .models import Cuota, Pago


class CuotaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cuota
        fields = ("id", "privada", "clave", "cuenta", "categoria", "descripcion", "nombre", "monto", "fecha_vencimiento", "status")


class PagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pago
        fields = ("id", "num", "cuota", "pagador", "privada", "monto", "estado", "comprobante", "fecha_pago", "fecha_validacion", "validador")
