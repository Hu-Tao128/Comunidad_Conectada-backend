import django_filters
from .models import Reservacion


class ReservacionFilter(django_filters.FilterSet):
    privada = django_filters.UUIDFilter(field_name="area__privada_id")

    class Meta:
        model = Reservacion
        fields = ("privada", "area", "usuario", "estado", "fecha", "status")
