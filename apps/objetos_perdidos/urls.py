from rest_framework.routers import DefaultRouter

from .views import EntregaViewSet, ObjetoPerdidoViewSet, ReclamacionViewSet

router = DefaultRouter()
router.register("objetos-perdidos", ObjetoPerdidoViewSet, basename="objeto-perdido")
router.register("reclamaciones-objetos", ReclamacionViewSet, basename="reclamacion-objeto")
router.register("entregas-objetos", EntregaViewSet, basename="entrega-objeto")
urlpatterns = router.urls
