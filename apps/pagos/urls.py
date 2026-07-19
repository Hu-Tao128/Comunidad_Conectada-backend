from rest_framework.routers import DefaultRouter
from .views import CuotaViewSet, PagoViewSet

router = DefaultRouter()
router.register("cuotas", CuotaViewSet, basename="cuota")
router.register("pagos", PagoViewSet, basename="pago")
urlpatterns = router.urls

