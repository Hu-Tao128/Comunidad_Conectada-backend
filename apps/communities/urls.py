from rest_framework.routers import DefaultRouter
from django.urls import path

from .views import (
    CasaViewSet,
    CrearPrivadaView,
    MisPrivadasView,
    ModuloViewSet,
    ModuloSistemaViewSet,
    AdminModulosView,
    AdminPrivadasView,
    AdminPrivadaModulosView,
    PrivadaViewSet,
    PromoverModeradorView,
    UnirsePrivadaView,
)

router = DefaultRouter()
router.register("privadas", PrivadaViewSet, basename="privada")
router.register("modulos", ModuloViewSet, basename="modulo")
router.register("casas", CasaViewSet, basename="casa")
router.register("modulos-sistema", ModuloSistemaViewSet, basename="modulo-sistema")
urlpatterns = [
    path("admin/privadas/", AdminPrivadasView.as_view(), name="admin-privadas"),
    path("admin/modulos/", AdminModulosView.as_view(), name="admin-modulos"),
    path("admin/privadas/<uuid:privada_id>/modulos/", AdminPrivadaModulosView.as_view(), name="admin-privada-modulos"),
    path("privadas/mias/", MisPrivadasView.as_view(), name="mis-privadas"),
    path("privadas/crear/", CrearPrivadaView.as_view(), name="crear-privada"),
    path("privadas/unirse/", UnirsePrivadaView.as_view(), name="unirse-privada"),
    path("privadas/<uuid:privada_id>/miembros/<uuid:usuario_id>/promover/", PromoverModeradorView.as_view(), name="promover-moderador"),
]
urlpatterns += router.urls
