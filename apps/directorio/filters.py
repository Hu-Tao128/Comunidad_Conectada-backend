import django_filters

from .models import Directorio


class DirectorioFilter(django_filters.FilterSet):
    class Meta:
        model = Directorio
        fields = ("privada", "categorias", "status")
