from common.mixins import PrivateScopedViewSet
from .filters import CuotaFilter, PagoFilter
from .permissions import PagosReadPermission
from .models import Cuota, Pago
from .serializers import CuotaSerializer, PagoSerializer


class CuotaViewSet(PrivateScopedViewSet):
    queryset = Cuota.objects.filter(status="activo", deleted_at__isnull=True).select_related("privada")
    serializer_class = CuotaSerializer
    permission_classes = (PagosReadPermission,)
    filterset_class = CuotaFilter
    search_fields = ("nombre", "clave")
    ordering_fields = ("fecha_vencimiento", "monto")


class PagoViewSet(PrivateScopedViewSet):
    queryset = Pago.objects.filter(status="activo", deleted_at__isnull=True).select_related("cuota", "cuota__privada", "pagador", "privada", "validador")
    serializer_class = PagoSerializer
    permission_classes = (PagosReadPermission,)
    filterset_class = PagoFilter
    search_fields = ("pagador__username", "cuota__nombre")
    ordering_fields = ("created_at", "monto", "pagado_en")
