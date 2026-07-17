import django_filters
from .models import AreaComunitaria


class AreaFilter(django_filters.FilterSet):
    class Meta:
        model = AreaComunitaria
        fields = ("privada", "status")
