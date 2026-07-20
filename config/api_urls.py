"""Rutas versionables de la API REST."""

from django.urls import include, path
from apps.auth.views import TokenObtainPairEmailView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("auth/token/", TokenObtainPairEmailView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("", include("apps.accounts.urls")),
    path("", include("apps.communities.urls")),
    path("", include("apps.directorio.urls")),
    path("", include("apps.areas.urls")),
    path("", include("apps.reservas.urls")),
    path("", include("apps.pagos.urls")),
    path("", include("apps.reportes.urls")),
    path("", include("apps.objetos_perdidos.urls")),
    path("", include("apps.proyectos.urls")),
]
