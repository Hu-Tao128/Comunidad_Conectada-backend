from django.db import transaction
from django.db.models import Max, Q
from rest_framework import mixins, viewsets

from apps.communities.models import PrivadaMiembro, RolPrivada
from .filters import ReservacionFilter
from .permissions import ReservacionReadPermission
from .models import Reservacion
from .serializers import ReservacionSerializer


class ReservacionViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = Reservacion.objects.filter(status="activo", deleted_at__isnull=True).select_related("area", "area__privada", "usuario", "usuario__perfil")
    serializer_class = ReservacionSerializer
    permission_classes = (ReservacionReadPermission,)
    filterset_class = ReservacionFilter
    search_fields = ("descripcion", "area__nombre", "usuario__username", "usuario__email")
    ordering_fields = ("fecha", "hora_inicio", "created_at")

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_staff:
            return queryset
        moderadas = PrivadaMiembro.objects.filter(
            usuario=self.request.user,
            rol=RolPrivada.MODERADOR,
            status="activo",
            deleted_at__isnull=True,
        ).values("privada_id")
        return queryset.filter(Q(usuario=self.request.user) | Q(area__privada_id__in=moderadas)).distinct()

    @transaction.atomic
    def perform_create(self, serializer):
        ultimo_folio = Reservacion.all_objects.aggregate(max_folio=Max("folio"))["max_folio"] or 0
        serializer.save(
            folio=ultimo_folio + 1,
            usuario=self.request.user,
            created_by=self.request.user,
            updated_by=self.request.user,
        )
