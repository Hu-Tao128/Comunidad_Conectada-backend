from django.db import transaction
from django.db.models import Max, Q
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied, ValidationError

from apps.communities.models import PrivadaMiembro, RolPrivada
from common.choices import EstadoReservacion
from common.mixins import PrivateScopedModelViewSet
from .filters import ReservacionFilter
from .permissions import ReservacionReadPermission
from .models import Reservacion
from .serializers import ReservacionSerializer


class ReservacionViewSet(PrivateScopedModelViewSet):
    private_lookup = "area__privada_id"
    queryset = Reservacion.objects.filter(
        status="activo", deleted_at__isnull=True
    ).select_related("area", "area__privada", "usuario", "usuario__perfil")
    serializer_class = ReservacionSerializer
    permission_classes = (ReservacionReadPermission,)
    filterset_class = ReservacionFilter
    search_fields = (
        "descripcion",
        "area__nombre",
        "usuario__username",
        "usuario__email",
    )
    ordering_fields = ("fecha", "hora_inicio", "created_at")
    http_method_names = ("get", "post", "patch", "delete", "head", "options")

    def _es_moderador(self, privada_id):
        return (
            self.request.user.is_staff
            or PrivadaMiembro.objects.filter(
                privada_id=privada_id,
                usuario=self.request.user,
                rol=RolPrivada.MODERADOR,
                status="activo",
                deleted_at__isnull=True,
            ).exists()
        )

    def _validar_disponibilidad(self, *, area, fecha, inicio, fin, excluir_id=None):
        reservas = Reservacion.all_objects.select_for_update().filter(
            area=area,
            fecha=fecha,
            status="activo",
            deleted_at__isnull=True,
            estado__in=(EstadoReservacion.PENDIENTE, EstadoReservacion.APROBADA),
        )
        if excluir_id:
            reservas = reservas.exclude(id=excluir_id)
        if reservas.filter(Q(hora_inicio__lt=fin) & Q(hora_fin__gt=inicio)).exists():
            raise ValidationError("El área ya tiene una reservación en ese horario.")

    @transaction.atomic
    def perform_create(self, serializer):
        area = serializer.validated_data["area"]
        if not PrivadaMiembro.objects.filter(
            privada=area.privada,
            usuario=self.request.user,
            status="activo",
            deleted_at__isnull=True,
        ).exists():
            raise PermissionDenied("No perteneces a la privada de esta área.")

        fecha = serializer.validated_data["fecha"]
        inicio = serializer.validated_data["hora_inicio"]
        fin = serializer.validated_data["hora_fin"]
        self._validar_disponibilidad(area=area, fecha=fecha, inicio=inicio, fin=fin)

        ultimo_folio = (
            Reservacion.all_objects.select_for_update().aggregate(
                max_folio=Max("folio")
            )["max_folio"]
            or 0
        )
        serializer.save(
            folio=ultimo_folio + 1,
            usuario=self.request.user,
            created_by=self.request.user,
            updated_by=self.request.user,
        )

    @transaction.atomic
    def perform_update(self, serializer):
        reservacion = self.get_object()
        es_moderador = self._es_moderador(reservacion.area.privada_id)
        if reservacion.usuario_id != self.request.user.id and not es_moderador:
            raise PermissionDenied(
                "Solo quien creó la reservación o un moderador puede modificarla."
            )

        cambios = set(serializer.validated_data)
        if "estado" in cambios and not es_moderador:
            raise PermissionDenied(
                "Solo un moderador puede cambiar el estado de la reservación."
            )
        if not es_moderador and reservacion.estado != EstadoReservacion.PENDIENTE:
            raise ValidationError("Solo se pueden editar reservaciones pendientes.")
        self._validar_disponibilidad(
            area=reservacion.area,
            fecha=serializer.validated_data.get("fecha", reservacion.fecha),
            inicio=serializer.validated_data.get(
                "hora_inicio", reservacion.hora_inicio
            ),
            fin=serializer.validated_data.get("hora_fin", reservacion.hora_fin),
            excluir_id=reservacion.id,
        )
        serializer.save(updated_by=self.request.user)

    def perform_destroy(self, instance):
        if instance.usuario_id != self.request.user.id and not self._es_moderador(
            instance.area.privada_id
        ):
            raise PermissionDenied(
                "Solo quien creó la reservación o un moderador puede cancelarla."
            )
        instance.estado = EstadoReservacion.CANCELADA
        instance.status = "eliminado"
        instance.deleted_at = timezone.now()
        instance.updated_by = self.request.user
        instance.save(
            update_fields=("estado", "status", "deleted_at", "updated_by", "updated_at")
        )
