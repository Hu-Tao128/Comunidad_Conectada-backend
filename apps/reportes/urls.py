from rest_framework.routers import DefaultRouter
from .views import IncidenteViewSet, ReporteViewSet

router = DefaultRouter()
router.register("reportes", ReporteViewSet, basename="reporte")
router.register("incidentes", IncidenteViewSet, basename="incidente")
urlpatterns = router.urls

