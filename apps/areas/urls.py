from rest_framework.routers import DefaultRouter
from .views import AreaViewSet

router = DefaultRouter()
router.register("areas", AreaViewSet, basename="area")
urlpatterns = router.urls

