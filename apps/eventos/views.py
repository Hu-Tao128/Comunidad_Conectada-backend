from django.utils import timezone
from rest_framework.exceptions import PermissionDenied

from apps.communities.models import PrivadaMiembro, RolPrivada
from common.mixins import PrivateScopedModelViewSet

from .filters import EventoFilter
from .models import Evento
from .permissions import EventoPermission
from .serializers import EventoSerializer


class EventoViewSet(PrivateScopedModelViewSet):
    queryset = Evento.objects.filter(status="activo", deleted_at__isnull=True).select_related("privada", "created_by")
    serializer_class = EventoSerializer
    permission_classes = (EventoPermission,)
    filterset_class = EventoFilter
    search_fields = ("titulo", "descripcion", "ubicacion")
    ordering_fields = ("fecha_inicio", "titulo", "created_at")
    http_method_names = ("get", "post", "patch", "delete", "head", "options")

    def _puede_administrar(self, privada_id):
        return self.request.user.is_staff or PrivadaMiembro.objects.filter(
            privada_id=privada_id,
            usuario=self.request.user,
            rol=RolPrivada.MODERADOR,
            status="activo",
            deleted_at__isnull=True,
        ).exists()

    def perform_create(self, serializer):
        privada = serializer.validated_data["privada"]
        if not self._puede_administrar(privada.id):
            raise PermissionDenied("Solo un moderador puede crear eventos.")
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        evento = self.get_object()
        privada = serializer.validated_data.get("privada", evento.privada)
        if not self._puede_administrar(evento.privada_id) or not self._puede_administrar(privada.id):
            raise PermissionDenied("Solo un moderador puede editar eventos.")
        serializer.save(updated_by=self.request.user)

    def perform_destroy(self, instance):
        if not self._puede_administrar(instance.privada_id):
            raise PermissionDenied("Solo un moderador puede eliminar eventos.")
        instance.status = "eliminado"
        instance.deleted_at = timezone.now()
        instance.updated_by = self.request.user
        instance.save(update_fields=("status", "deleted_at", "updated_by", "updated_at"))
