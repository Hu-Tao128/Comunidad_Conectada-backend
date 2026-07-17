import django_filters
from .models import Reservacion


class ReservacionFilter(django_filters.FilterSet):
    class Meta:
        model = Reservacion
        fields = ("area", "usuario", "estado", "fecha", "status")
