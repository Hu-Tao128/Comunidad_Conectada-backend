import django_filters
from .models import Proyecto


class ProyectoFilter(django_filters.FilterSet):
    class Meta:
        model = Proyecto
        fields = ("privada", "estado", "fecha_inicio", "fecha_fin")

