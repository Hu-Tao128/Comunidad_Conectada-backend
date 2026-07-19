from common.mixins import ReadOnlyViewSet
from .filters import ReservacionFilter
from .permissions import ReservacionReadPermission
from .models import Reservacion
from .serializers import ReservacionSerializer


class ReservacionViewSet(ReadOnlyViewSet):
    queryset = Reservacion.objects.filter(status="activo", deleted_at__isnull=True).select_related("area", "area__privada", "usuario")
    serializer_class = ReservacionSerializer
    permission_classes = (ReservacionReadPermission,)
    filterset_class = ReservacionFilter
    search_fields = ("descripcion", "area__nombre", "usuario__username")
    ordering_fields = ("fecha", "hora_inicio", "created_at")
