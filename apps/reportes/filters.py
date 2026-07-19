import django_filters
from .models import Incidente, Reporte


class ReporteFilter(django_filters.FilterSet):
    class Meta:
        model = Reporte
        fields = ("privada", "creador", "supervisor", "estado", "status")


class IncidenteFilter(django_filters.FilterSet):
    class Meta:
        model = Incidente
        fields = ("reporte", "tipo")
