"""URLs para cuentas de usuario."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import UsuarioViewSet, UsuarioMeView

router = DefaultRouter()
router.register("usuarios", UsuarioViewSet, basename="usuario")

urlpatterns = [
    path("usuarios/me/", UsuarioMeView.as_view(), name="usuario-me"),
    path("", include(router.urls)),
]
