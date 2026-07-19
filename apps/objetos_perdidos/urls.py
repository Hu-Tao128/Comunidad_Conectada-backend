from rest_framework.routers import DefaultRouter
from .views import ObjetoPerdidoViewSet

router = DefaultRouter()
router.register("objetos-perdidos", ObjetoPerdidoViewSet, basename="objeto-perdido")
urlpatterns = router.urls

