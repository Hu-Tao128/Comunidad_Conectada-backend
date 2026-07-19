from rest_framework.routers import DefaultRouter

from .views import DirectorioViewSet

router = DefaultRouter()
router.register("directorio", DirectorioViewSet, basename="directorio")
urlpatterns = router.urls

