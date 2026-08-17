from django.utils import timezone
from rest_framework.exceptions import PermissionDenied

from apps.communities.models import PrivadaMiembro, RolPrivada
from common.mixins import PrivateScopedModelViewSet

from .filters import DirectorioFilter
from .models import Directorio
from .permissions import DirectorioReadPermission
from .serializers import DirectorioSerializer


class DirectorioViewSet(PrivateScopedModelViewSet):
    queryset = Directorio.objects.filter(status="activo", deleted_at__isnull=True).select_related("privada", "created_by")
    serializer_class = DirectorioSerializer
    permission_classes = (DirectorioReadPermission,)
    filterset_class = DirectorioFilter
    search_fields = ("nombre", "categorias", "descripcion", "codigo")
    ordering_fields = ("nombre", "created_at")
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
            raise PermissionDenied("Solo un moderador puede crear entradas del directorio.")
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        entrada = self.get_object()
        privada = serializer.validated_data.get("privada", entrada.privada)
        if not self._puede_administrar(entrada.privada_id) or not self._puede_administrar(privada.id):
            raise PermissionDenied("Solo un moderador puede editar entradas del directorio.")
        serializer.save(updated_by=self.request.user)

    def perform_destroy(self, instance):
        if not self._puede_administrar(instance.privada_id):
            raise PermissionDenied("Solo un moderador puede eliminar entradas del directorio.")
        instance.status = "eliminado"
        instance.deleted_at = timezone.now()
        instance.updated_by = self.request.user
        instance.save(update_fields=("status", "deleted_at", "updated_by", "updated_at"))
