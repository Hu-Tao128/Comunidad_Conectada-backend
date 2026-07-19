"""Mixins comunes para la API."""

from rest_framework import mixins, viewsets


class ReadOnlyViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """ViewSet base que expone solamente GET de lista y detalle."""

