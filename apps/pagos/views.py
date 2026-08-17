from django.db.models import Count, Q
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response

from apps.communities.models import PrivadaMiembro, RolPrivada
from common.choices import EstadoPago
from .filters import CuotaFilter, PagoFilter
from .models import Cuota, Pago
from .permissions import PagosPermission
from .serializers import CuotaSerializer, PagoSerializer, SubirComprobanteSerializer, ValidarPagoSerializer
from .services import actualizar_vencidos, crear_cuota_con_pagos, registrar_comprobante, validar_pago


def privadas_del_usuario(user):
    return PrivadaMiembro.objects.filter(
        usuario=user, status="activo", deleted_at__isnull=True
    ).values("privada_id")


class CuotaViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = Cuota.objects.filter(status="activo", deleted_at__isnull=True).select_related("privada")
    serializer_class = CuotaSerializer
    permission_classes = (PagosPermission,)
    filterset_class = CuotaFilter
    search_fields = ("nombre", "clave", "descripcion", "categoria")
    ordering_fields = ("fecha_vencimiento", "monto", "created_at")

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_staff:
            return queryset
        return queryset.filter(privada_id__in=privadas_del_usuario(self.request.user))

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cuota = crear_cuota_con_pagos(datos=serializer.validated_data, moderador=request.user)
        return Response(self.get_serializer(cuota).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=("get",))
    def resumen(self, request, pk=None):
        cuota = self.get_object()
        pagos = Pago.objects.filter(cuota=cuota, status="activo", deleted_at__isnull=True)
        actualizar_vencidos(pagos)
        conteos = {estado: 0 for estado in EstadoPago.values}
        conteos.update(dict(pagos.values_list("estado").annotate(total=Count("id")).values_list("estado", "total")))
        return Response({"total": pagos.count(), "estados": conteos})


class PagoViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Pago.objects.filter(status="activo", deleted_at__isnull=True).select_related(
        "cuota", "cuota__privada", "pagador", "pagador__perfil", "privada", "validador"
    ).prefetch_related("intentos", "intentos__validador")
    serializer_class = PagoSerializer
    permission_classes = (PagosPermission,)
    filterset_class = PagoFilter
    search_fields = ("pagador__username", "pagador__email", "pagador__first_name", "pagador__last_name", "cuota__nombre")
    ordering_fields = ("created_at", "fecha_pago", "cuota__fecha_vencimiento")

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_staff:
            actualizar_vencidos(queryset)
            return queryset
        privadas_moderadas = PrivadaMiembro.objects.filter(
            usuario=self.request.user,
            rol=RolPrivada.MODERADOR,
            status="activo",
            deleted_at__isnull=True,
        ).values("privada_id")
        queryset = queryset.filter(Q(pagador=self.request.user) | Q(privada_id__in=privadas_moderadas)).distinct()
        actualizar_vencidos(queryset)
        return queryset

    @action(detail=False, methods=("get",))
    def resumen(self, request):
        pagos = self.filter_queryset(self.get_queryset())
        conteos = {estado: 0 for estado in EstadoPago.values}
        conteos.update(dict(pagos.values_list("estado").annotate(total=Count("id")).values_list("estado", "total")))
        return Response({"total": pagos.count(), "estados": conteos})

    @action(detail=True, methods=("post",), parser_classes=(MultiPartParser, FormParser), url_path="comprobante")
    def comprobante(self, request, pk=None):
        pago = self.get_object()
        serializer = SubirComprobanteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        registrar_comprobante(pago=pago, archivo=serializer.validated_data["comprobante"], usuario=request.user)
        pago.refresh_from_db()
        return Response(self.get_serializer(pago).data)

    @action(detail=True, methods=("post",), url_path="validar")
    def validar(self, request, pk=None):
        pago = self.get_object()
        serializer = ValidarPagoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        pago = validar_pago(
            pago=pago,
            estado=serializer.validated_data["estado"],
            motivo=serializer.validated_data.get("motivo", ""),
            moderador=request.user,
        )
        return Response(self.get_serializer(pago).data)
