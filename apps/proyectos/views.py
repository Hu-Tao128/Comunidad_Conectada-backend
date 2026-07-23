from common.mixins import PrivateScopedViewSet
from .filters import ProyectoFilter
from .permissions import ProyectoReadPermission
from .models import Proyecto
from .serializers import ProyectoSerializer


class ProyectoViewSet(PrivateScopedViewSet):
    queryset = Proyecto.objects.filter(status="activo", deleted_at__isnull=True).select_related("privada", "usuario")
    serializer_class = ProyectoSerializer
    permission_classes = (ProyectoReadPermission,)
    filterset_class = ProyectoFilter
    search_fields = ("nombre", "descripcion")
    ordering_fields = ("created_at", "nombre", "estado")
