import django_filters
from .models import Cuota, Pago


class CuotaFilter(django_filters.FilterSet):
    class Meta:
        model = Cuota
        fields = ("privada", "fecha_vencimiento")


class PagoFilter(django_filters.FilterSet):
    class Meta:
        model = Pago
        fields = ("cuota", "pagador", "privada", "estado", "num", "status")
