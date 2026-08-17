from django.db import transaction
from django.db.models import Max
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated

from apps.communities.models import PrivadaMiembro, RolPrivada
from .models import Minuta
from .serializers import MinutaSerializer


class MinutaViewSet(viewsets.ModelViewSet):
    serializer_class = MinutaSerializer
    permission_classes = (IsAuthenticated,)
    filterset_fields = ("privada", "tipo_reunion")
    search_fields = ("titulo", "objetivo", "acuerdos", "lugar")
    ordering_fields = ("fecha_reunion", "created_at", "numero")
    http_method_names = ("get", "post", "patch", "head", "options")

    def get_queryset(self):
        queryset = Minuta.objects.select_related("privada", "moderador", "moderador__perfil").filter(
            status="activo", deleted_at__isnull=True
        )
        if self.request.user.is_staff:
            return queryset
        privadas = PrivadaMiembro.objects.filter(
            usuario=self.request.user, status="activo", deleted_at__isnull=True
        ).values("privada_id")
        return queryset.filter(privada_id__in=privadas)

    def _es_moderador(self, privada):
        return self.request.user.is_staff or PrivadaMiembro.objects.filter(
            privada=privada, usuario=self.request.user, rol=RolPrivada.MODERADOR,
            status="activo", deleted_at__isnull=True,
        ).exists()

    @transaction.atomic
    def perform_create(self, serializer):
        privada = serializer.validated_data["privada"]
        if not self._es_moderador(privada):
            raise PermissionDenied("Solo un moderador activo puede crear minutas.")
        numero = (Minuta.all_objects.select_for_update().filter(privada=privada).aggregate(maximo=Max("numero"))["maximo"] or 0) + 1
        serializer.save(numero=numero, moderador=self.request.user, created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        minuta = self.get_object()
        if not self._es_moderador(minuta.privada):
            raise PermissionDenied("Solo un moderador activo puede editar minutas.")
        serializer.save(updated_by=self.request.user)
