from common.mixins import PrivateScopedViewSet
from .filters import ObjetoPerdidoFilter
from .permissions import ObjetosPerdidosReadPermission
from .models import ObjetoPerdido
from .serializers import ObjetoPerdidoSerializer


class ObjetoPerdidoViewSet(PrivateScopedViewSet):
    queryset = ObjetoPerdido.objects.filter(status="activo", deleted_at__isnull=True).select_related("privada", "reportado_por", "recuperador")
    serializer_class = ObjetoPerdidoSerializer
    permission_classes = (ObjetosPerdidosReadPermission,)
    filterset_class = ObjetoPerdidoFilter
    search_fields = ("nombre", "descripcion", "tipo")
    ordering_fields = ("created_at", "nombre", "tipo")
