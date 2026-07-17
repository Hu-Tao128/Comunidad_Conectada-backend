from rest_framework.routers import DefaultRouter
from .views import ReservacionViewSet

router = DefaultRouter()
router.register("reservaciones", ReservacionViewSet, basename="reservacion")
urlpatterns = router.urls

