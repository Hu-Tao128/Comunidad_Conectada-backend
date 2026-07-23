"""Mixins comunes para la API."""

from rest_framework import mixins, viewsets

from apps.communities.models import PrivadaMiembro


class ReadOnlyViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """ViewSet base que expone solamente GET de lista y detalle."""


class PrivateScopedViewSet(ReadOnlyViewSet):
    """Limita los datos a las privadas del usuario autenticado."""

    private_lookup = "privada_id"

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_staff:
            return queryset
        private_ids = PrivadaMiembro.objects.filter(
            usuario=self.request.user,
            status="activo",
            deleted_at__isnull=True,
        ).values("privada_id")
        return queryset.filter(**{f"{self.private_lookup}__in": private_ids})
