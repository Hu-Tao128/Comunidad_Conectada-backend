from rest_framework.routers import DefaultRouter
from .views import CasaViewSet, ModuloViewSet, PrivadaViewSet

router = DefaultRouter()
router.register("privadas", PrivadaViewSet, basename="privada")
router.register("modulos", ModuloViewSet, basename="modulo")
router.register("casas", CasaViewSet, basename="casa")
urlpatterns = router.urls
