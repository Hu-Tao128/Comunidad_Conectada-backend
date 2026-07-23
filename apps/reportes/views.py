from common.mixins import PrivateScopedViewSet
from .filters import IncidenteFilter, ReporteFilter
from .permissions import ReportesReadPermission
from .models import Incidente, Reporte
from .serializers import IncidenteSerializer, ReporteSerializer


class ReporteViewSet(PrivateScopedViewSet):
    queryset = Reporte.objects.filter(status="activo", deleted_at__isnull=True).select_related("privada", "creador", "supervisor").prefetch_related("incidentes")
    serializer_class = ReporteSerializer
    permission_classes = (ReportesReadPermission,)
    filterset_class = ReporteFilter
    search_fields = ("titulo", "descripcion")
    ordering_fields = ("created_at", "estado")


class IncidenteViewSet(PrivateScopedViewSet):
    queryset = Incidente.objects.filter(status="activo", deleted_at__isnull=True).select_related("reporte", "usuario", "privada")
    serializer_class = IncidenteSerializer
    permission_classes = (ReportesReadPermission,)
    filterset_class = IncidenteFilter
    search_fields = ("ubicacion", "tipo", "reporte__titulo")
    ordering_fields = ("created_at", "tipo")
