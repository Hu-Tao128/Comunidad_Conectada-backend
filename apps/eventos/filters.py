import django_filters

from .models import Evento


class EventoFilter(django_filters.FilterSet):
    fecha_desde = django_filters.DateTimeFilter(field_name="fecha_inicio", lookup_expr="gte")
    fecha_hasta = django_filters.DateTimeFilter(field_name="fecha_inicio", lookup_expr="lte")

    class Meta:
        model = Evento
        fields = ("privada", "status", "fecha_desde", "fecha_hasta")
