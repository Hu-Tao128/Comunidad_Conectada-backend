from common.mixins import ReadOnlyViewSet
from .models import Casa, Modulo, Privada
from .serializers import CasaSerializer, ModuloSerializer, PrivadaSerializer


class PrivadaViewSet(ReadOnlyViewSet):
    queryset = Privada.objects.select_related("creador").filter(status="activo", deleted_at__isnull=True)
    serializer_class = PrivadaSerializer
    search_fields = ("codigo", "nombre", "dir_ciudad")
    ordering_fields = ("nombre", "codigo")


class ModuloViewSet(ReadOnlyViewSet):
    queryset = Modulo.objects.select_related("privada").filter(status="activo", deleted_at__isnull=True)
    serializer_class = ModuloSerializer
    search_fields = ("nombre", "privada__nombre")
    ordering_fields = ("nombre",)


class CasaViewSet(ReadOnlyViewSet):
    queryset = Casa.objects.select_related("modulo", "modulo__privada").filter(status="activo", deleted_at__isnull=True)
    serializer_class = CasaSerializer
    search_fields = ("numero", "modulo__nombre")
    ordering_fields = ("numero",)
