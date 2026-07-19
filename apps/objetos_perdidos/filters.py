import django_filters
from .models import ObjetoPerdido


class ObjetoPerdidoFilter(django_filters.FilterSet):
    class Meta:
        model = ObjetoPerdido
        fields = ("privada", "reportado_por", "tipo", "status")
