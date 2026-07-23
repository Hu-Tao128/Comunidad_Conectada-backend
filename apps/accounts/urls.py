"""URLs para cuentas de usuario."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AdminUsuariosView, CambiarPasswordView, PerfilMeView, RegistroView, UsuarioViewSet, UsuarioMeView

router = DefaultRouter()
router.register("usuarios", UsuarioViewSet, basename="usuario")

urlpatterns = [
    path("auth/register/", RegistroView.as_view(), name="registro"),
    path("usuarios/me/", UsuarioMeView.as_view(), name="usuario-me"),
    path("perfiles/me/", PerfilMeView.as_view(), name="perfil-me"),
    path("usuarios/me/password/", CambiarPasswordView.as_view(), name="cambiar-password"),
    path("admin/usuarios/", AdminUsuariosView.as_view(), name="admin-usuarios"),
    path("", include(router.urls)),
]
