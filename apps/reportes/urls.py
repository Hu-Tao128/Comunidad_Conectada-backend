from rest_framework.routers import DefaultRouter
from .views import IncidenteViewSet, ReporteViewSet, TipoReporteViewSet

router = DefaultRouter()
router.register("reportes", ReporteViewSet, basename="reporte")
router.register("incidentes", IncidenteViewSet, basename="incidente")
router.register("tipos-reporte", TipoReporteViewSet, basename="tipo-reporte")
urlpatterns = router.urls

