from django.db import transaction
from django.db.models import Max
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.communities.models import PrivadaMiembro, RolPrivada
from common.choices import EstadoIncidente
from .filters import IncidenteFilter, ReporteFilter
from .models import EstadoReporte, Incidente, Reporte, TipoReporte
from .serializers import IncidenteSerializer, ReporteSerializer, TipoReporteSerializer


def membresias_activas(usuario):
    return PrivadaMiembro.objects.filter(usuario=usuario, status="activo", deleted_at__isnull=True)


class TipoReporteViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TipoReporte.objects.filter(status="activo", deleted_at__isnull=True)
    serializer_class = TipoReporteSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = None


class IncidenteViewSet(viewsets.ModelViewSet):
    serializer_class = IncidenteSerializer
    permission_classes = (IsAuthenticated,)
    filterset_class = IncidenteFilter
    search_fields = ("titulo", "descripcion", "ubicacion", "usuario__email")
    ordering_fields = ("created_at", "fecha_incidente", "prioridad", "estado")
    http_method_names = ("get", "post", "patch", "head", "options")

    def get_queryset(self):
        queryset = Incidente.objects.select_related(
            "privada", "usuario", "usuario__perfil", "tipo_categoria"
        ).filter(status="activo", deleted_at__isnull=True)
        if self.request.user.is_staff:
            return queryset
        membresias = membresias_activas(self.request.user)
        moderadas = membresias.filter(rol=RolPrivada.MODERADOR).values("privada_id")
        propias = membresias.values("privada_id")
        from django.db.models import Q
        return queryset.filter(Q(privada_id__in=moderadas) | Q(privada_id__in=propias, usuario=self.request.user)).distinct()

    @transaction.atomic
    def perform_create(self, serializer):
        privada = serializer.validated_data["privada"]
        if not PrivadaMiembro.objects.filter(
            privada=privada, usuario=self.request.user, rol=RolPrivada.HABITANTE,
            status="activo", deleted_at__isnull=True,
        ).exists():
            raise PermissionDenied("Solo un habitante activo puede registrar incidentes en esta privada.")
        ultimo = Incidente.all_objects.select_for_update().aggregate(max_num=Max("num"))["max_num"] or 0
        serializer.save(num=ultimo + 1, usuario=self.request.user,
                        created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        incidente = self.get_object()
        if incidente.usuario_id != self.request.user.id:
            raise PermissionDenied("Solo el habitante que creó el incidente puede editarlo.")
        if incidente.reportes_seguimiento.filter(status="activo", deleted_at__isnull=True).exists():
            raise ValidationError("El incidente ya no puede editarse porque tiene un reporte de seguimiento.")
        serializer.save(updated_by=self.request.user)


class ReporteViewSet(viewsets.ModelViewSet):
    serializer_class = ReporteSerializer
    permission_classes = (IsAuthenticated,)
    filterset_class = ReporteFilter
    search_fields = ("titulo", "descripcion", "incidente__titulo", "creador__email")
    ordering_fields = ("created_at", "estado", "prioridad", "fecha_suceso")
    http_method_names = ("get", "post", "patch", "head", "options")

    def get_queryset(self):
        queryset = Reporte.objects.select_related(
            "privada", "creador", "creador__perfil", "tipo_categoria", "incidente",
            "incidente__usuario", "incidente__usuario__perfil", "incidente__tipo_categoria",
        ).filter(status="activo", deleted_at__isnull=True)
        if self.request.user.is_staff:
            return queryset
        membresias = membresias_activas(self.request.user)
        moderadas = membresias.filter(rol=RolPrivada.MODERADOR).values("privada_id")
        propias = membresias.values("privada_id")
        from django.db.models import Q
        return queryset.filter(Q(privada_id__in=moderadas) | Q(privada_id__in=propias, incidente__usuario=self.request.user)).distinct()

    @transaction.atomic
    def perform_create(self, serializer):
        incidente = serializer.validated_data["incidente"]
        if not PrivadaMiembro.objects.filter(
            privada=incidente.privada, usuario=self.request.user, rol=RolPrivada.MODERADOR,
            status="activo", deleted_at__isnull=True,
        ).exists():
            raise PermissionDenied("Solo un moderador activo puede crear reportes para esta privada.")
        ultimo = Reporte.all_objects.select_for_update().aggregate(max_num=Max("num"))["max_num"] or 0
        reporte = serializer.save(
            num=ultimo + 1, privada=incidente.privada, creador=self.request.user,
            tipo_categoria=incidente.tipo_categoria, prioridad=incidente.prioridad,
            fecha_suceso=incidente.fecha_incidente,
            created_by=self.request.user, updated_by=self.request.user,
        )
        incidente.estado = EstadoIncidente.EN_PROCESO
        incidente.updated_by = self.request.user
        incidente.save(update_fields=("estado", "updated_by", "updated_at"))
        return reporte

    def perform_update(self, serializer):
        reporte = self.get_object()
        if reporte.estado == EstadoReporte.CONCLUIDO:
            raise ValidationError("Un reporte concluido ya no puede editarse.")
        if not PrivadaMiembro.objects.filter(
            privada=reporte.privada, usuario=self.request.user, rol=RolPrivada.MODERADOR,
            status="activo", deleted_at__isnull=True,
        ).exists():
            raise PermissionDenied("Solo un moderador puede actualizar el reporte.")
        serializer.save(updated_by=self.request.user)

    @action(detail=True, methods=("post",))
    def concluir(self, request, pk=None):
        reporte = self.get_object()
        if not PrivadaMiembro.objects.filter(
            privada=reporte.privada, usuario=request.user, rol=RolPrivada.MODERADOR,
            status="activo", deleted_at__isnull=True,
        ).exists():
            raise PermissionDenied("Solo un moderador puede concluir el reporte.")
        if reporte.estado == EstadoReporte.CONCLUIDO:
            raise ValidationError({"estado": "El reporte ya fue concluido."})
        reporte.estado = EstadoReporte.CONCLUIDO
        reporte.updated_by = request.user
        reporte.save(update_fields=("estado", "updated_by", "updated_at"))
        quedan_abiertos = reporte.incidente.reportes_seguimiento.filter(
            status="activo", deleted_at__isnull=True
        ).exclude(estado=EstadoReporte.CONCLUIDO).exists()
        reporte.incidente.estado = EstadoIncidente.EN_PROCESO if quedan_abiertos else EstadoIncidente.RESUELTO
        reporte.incidente.updated_by = request.user
        reporte.incidente.save(update_fields=("estado", "updated_by", "updated_at"))
        return Response(self.get_serializer(reporte).data, status=status.HTTP_200_OK)
