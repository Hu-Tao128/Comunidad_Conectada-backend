from django.db import transaction
from django.db.models import Max
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from common.mixins import PrivateScopedViewSet
from .filters import IncidenteFilter, ReporteFilter
from .permissions import ReportesReadPermission
from .models import EstadoReporte, Incidente, Reporte
from .serializers import IncidenteSerializer, ReporteSerializer


class ReporteViewSet(viewsets.ModelViewSet):
    queryset = Reporte.objects.filter(status="activo", deleted_at__isnull=True).select_related("privada", "creador", "supervisor").prefetch_related("incidentes")
    serializer_class = ReporteSerializer
    permission_classes = (ReportesReadPermission,)
    filterset_class = ReporteFilter
    search_fields = ("titulo", "descripcion")
    ordering_fields = ("created_at", "estado")

    def get_queryset(self):
        queryset = self.queryset
        if self.request.user.is_staff:
            return queryset
        from apps.communities.models import PrivadaMiembro

        private_ids = PrivadaMiembro.objects.filter(
            usuario=self.request.user,
            status="activo",
            deleted_at__isnull=True,
        ).values("privada_id")
        return queryset.filter(privada_id__in=private_ids)

    @transaction.atomic
    def perform_create(self, serializer):
        ultimo_numero = Reporte.all_objects.aggregate(max_num=Max("num"))["max_num"] or 0
        serializer.save(
            num=ultimo_numero + 1,
            creador=self.request.user,
            created_by=self.request.user,
            updated_by=self.request.user,
        )

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def perform_destroy(self, instance):
        instance.updated_by = self.request.user
        instance.save(update_fields=("updated_by", "updated_at"))
        instance.delete()

    @action(detail=False, methods=("get",), url_path="mis-reportes")
    def mis_reportes(self, request):
        queryset = self.filter_queryset(self.get_queryset().filter(creador=request.user))
        page = self.paginate_queryset(queryset)
        if page is not None:
            return self.get_paginated_response(self.get_serializer(page, many=True).data)
        return Response(self.get_serializer(queryset, many=True).data)

    @action(detail=True, methods=("post",))
    def concluir(self, request, pk=None):
        reporte = self.get_object()
        if reporte.estado == EstadoReporte.CONCLUIDO:
            raise ValidationError({"estado": "El reporte ya fue concluido."})
        if reporte.estado != EstadoReporte.PENDIENTE:
            raise ValidationError(
                {"estado": "Solo se pueden concluir reportes pendientes."}
            )

        reporte.estado = EstadoReporte.CONCLUIDO
        reporte.updated_by = request.user
        reporte.save(update_fields=("estado", "updated_by", "updated_at"))
        return Response(self.get_serializer(reporte).data, status=status.HTTP_200_OK)


class IncidenteViewSet(PrivateScopedViewSet):
    queryset = Incidente.objects.filter(status="activo", deleted_at__isnull=True).select_related("reporte", "usuario", "privada")
    serializer_class = IncidenteSerializer
    permission_classes = (ReportesReadPermission,)
    filterset_class = IncidenteFilter
    search_fields = ("ubicacion", "tipo", "reporte__titulo")
    ordering_fields = ("created_at", "tipo")
