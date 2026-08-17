import django_filters
from .models import Incidente, Reporte


class ReporteFilter(django_filters.FilterSet):
    class Meta:
        model = Reporte
        fields = ("privada", "creador", "incidente", "estado", "prioridad", "tipo_categoria", "status")


class IncidenteFilter(django_filters.FilterSet):
    class Meta:
        model = Incidente
        fields = ("privada", "usuario", "estado", "prioridad", "tipo_categoria")
