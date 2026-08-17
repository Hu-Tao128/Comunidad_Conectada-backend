from rest_framework.routers import DefaultRouter

from .views import MinutaViewSet

router = DefaultRouter()
router.register("minutas", MinutaViewSet, basename="minuta")
urlpatterns = router.urls
