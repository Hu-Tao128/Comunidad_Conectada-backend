import django_filters

from .models import Usuario


class UsuarioFilter(django_filters.FilterSet):
    class Meta:
        model = Usuario
        fields = ("is_active", "status", "username", "email")
