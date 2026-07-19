from common.mixins import ReadOnlyViewSet
from .models import AreaComunitaria
from .filters import AreaFilter
from .permissions import AreaReadPermission
from .serializers import AreaComunitariaSerializer


class AreaViewSet(ReadOnlyViewSet):
    queryset = AreaComunitaria.objects.filter(status="activo", deleted_at__isnull=True).select_related("privada")
    serializer_class = AreaComunitariaSerializer
    permission_classes = (AreaReadPermission,)
    filterset_class = AreaFilter
    search_fields = ("nombre", "descripcion")
    ordering_fields = ("nombre", "capacidad")
