from common.mixins import ReadOnlyViewSet

from .filters import DirectorioFilter
from .models import Directorio
from .permissions import DirectorioReadPermission
from .serializers import DirectorioSerializer


class DirectorioViewSet(ReadOnlyViewSet):
    queryset = Directorio.objects.filter(status="activo", deleted_at__isnull=True).select_related("privada", "created_by")
    serializer_class = DirectorioSerializer
    permission_classes = (DirectorioReadPermission,)
    filterset_class = DirectorioFilter
    search_fields = ("nombre", "categorias", "descripcion", "codigo")
    ordering_fields = ("nombre", "created_at")
