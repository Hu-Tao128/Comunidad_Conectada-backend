from datetime import timedelta

from django.db import transaction
from django.db.models import Max, Q
from django.utils import timezone
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response

from apps.communities.models import PrivadaMiembro, RolPrivada
from common.mixins import PrivateScopedModelViewSet

from .filters import ObjetoPerdidoFilter
from .models import EntregaObjeto, ObjetoPerdido, Reclamacion
from .permissions import ObjetosPerdidosPermission
from .serializers import EntregaSerializer, ObjetoPerdidoSerializer, ReclamacionSerializer


def es_moderador(user, privada_id):
    return user.is_staff or PrivadaMiembro.objects.filter(privada_id=privada_id, usuario=user, rol=RolPrivada.MODERADOR, status="activo", deleted_at__isnull=True).exists()


def es_miembro(user, privada_id):
    return user.is_staff or PrivadaMiembro.objects.filter(privada_id=privada_id, usuario=user, status="activo", deleted_at__isnull=True).exists()


class ObjetoPerdidoViewSet(PrivateScopedModelViewSet):
    queryset = ObjetoPerdido.objects.filter(status="activo", deleted_at__isnull=True).select_related("privada", "reportado_por", "reportado_por__perfil", "responsable_resguardo", "posible_localizador", "posible_localizador__perfil", "recuperador").prefetch_related("preguntas_validacion")
    serializer_class = ObjetoPerdidoSerializer
    permission_classes = (ObjetosPerdidosPermission,)
    filterset_class = ObjetoPerdidoFilter
    search_fields = ("nombre", "descripcion", "ubicacion", "informacion_adicional")
    ordering_fields = ("created_at", "nombre", "tipo", "estado_caso", "fecha_evento")
    http_method_names = ("get", "post", "patch", "delete", "head", "options")

    def get_queryset(self):
        queryset = super().get_queryset()
        finalizado = self.request.query_params.get("finalizado")
        finales = (ObjetoPerdido.EstadoCaso.RECUPERADO, ObjetoPerdido.EstadoCaso.ENTREGADO, ObjetoPerdido.EstadoCaso.CERRADO)
        if finalizado == "true":
            queryset = queryset.filter(estado_caso__in=finales)
        elif finalizado == "false":
            queryset = queryset.exclude(estado_caso__in=finales)
        return queryset

    @transaction.atomic
    def perform_create(self, serializer):
        privada = serializer.validated_data["privada"]
        if not es_miembro(self.request.user, privada.id):
            raise PermissionDenied("No perteneces a esta privada.")
        siguiente = (ObjetoPerdido.all_objects.select_for_update().aggregate(maximo=Max("num"))["maximo"] or 0) + 1
        responsable = self.request.user if serializer.validated_data.get("tipo") == ObjetoPerdido.Tipo.RESGUARDADO else None
        fecha_evento = serializer.validated_data.get("fecha_evento")
        serializer.save(num=siguiente, reportado_por=self.request.user, responsable_resguardo=responsable, fecha_reporte=fecha_evento.date() if fecha_evento else timezone.localdate(), created_by=self.request.user, updated_by=self.request.user)

    def _puede_gestionar(self, objeto):
        return es_moderador(self.request.user, objeto.privada_id) or self.request.user.id in {objeto.reportado_por_id, objeto.responsable_resguardo_id}

    def perform_update(self, serializer):
        objeto = self.get_object()
        if not self._puede_gestionar(objeto):
            raise PermissionDenied("No puedes modificar esta publicación.")
        serializer.save(updated_by=self.request.user)

    def perform_destroy(self, instance):
        if not self._puede_gestionar(instance):
            raise PermissionDenied("No puedes eliminar esta publicación.")
        instance.delete()

    @action(detail=True, methods=("post",), url_path="posiblemente-localizado")
    def posiblemente_localizado(self, request, pk=None):
        objeto = self.get_object()
        if objeto.tipo != ObjetoPerdido.Tipo.EXTRAVIADO or objeto.finalizado:
            raise ValidationError("El objeto no puede marcarse como localizado.")
        if objeto.posible_localizador_id:
            if objeto.posible_localizador_id == request.user.id:
                return Response(self.get_serializer(objeto).data)
            raise ValidationError("Otro habitante ya indicó que posiblemente encontró este objeto.")
        objeto.posible_localizador = request.user
        objeto.estado_caso = ObjetoPerdido.EstadoCaso.POSIBLEMENTE_LOCALIZADO
        objeto.fecha_encontrado = timezone.localdate()
        objeto.updated_by = request.user
        objeto.save()
        return Response(self.get_serializer(objeto).data)

    @action(detail=True, methods=("get",), url_path="preguntas-reclamacion")
    def preguntas_reclamacion(self, request, pk=None):
        objeto = self.get_object()
        if objeto.tipo != ObjetoPerdido.Tipo.RESGUARDADO or objeto.finalizado:
            raise ValidationError("El objeto no admite reclamaciones.")
        return Response([{"id": str(p.id), "pregunta": p.pregunta, "orden": p.orden} for p in objeto.preguntas_validacion.all()])

    @action(detail=True, methods=("post",), url_path="finalizar-extraviado")
    def finalizar_extraviado(self, request, pk=None):
        objeto = self.get_object()
        if objeto.tipo != ObjetoPerdido.Tipo.EXTRAVIADO or objeto.finalizado:
            raise ValidationError("Este objeto extraviado no puede finalizarse.")
        if objeto.reportado_por_id != request.user.id:
            raise PermissionDenied("Solo quien creó la publicación puede finalizarla.")
        if not objeto.posible_localizador_id:
            raise ValidationError("Aún nadie ha indicado que encontró el objeto.")
        objeto.estado_caso = ObjetoPerdido.EstadoCaso.RECUPERADO
        objeto.fecha_devuelto = timezone.localdate()
        objeto.recuperador = objeto.posible_localizador
        objeto.informacion_adicional = request.data.get("resultado", objeto.informacion_adicional)
        objeto.updated_by = request.user
        objeto.save()
        return Response(self.get_serializer(objeto).data)

    @action(detail=True, methods=("post",), url_path="finalizar-resguardado")
    def finalizar_resguardado(self, request, pk=None):
        objeto = self.get_object()
        if objeto.tipo != ObjetoPerdido.Tipo.RESGUARDADO or objeto.finalizado:
            raise ValidationError("Este objeto resguardado no puede finalizarse.")
        if objeto.reportado_por_id != request.user.id:
            raise PermissionDenied("Solo quien creó la publicación puede finalizarla.")
        reclamacion_id = request.data.get("reclamacion")
        reclamacion = objeto.reclamaciones.filter(id=reclamacion_id, estado=Reclamacion.Estado.APROBADA, status="activo").first()
        if not reclamacion:
            raise ValidationError({"reclamacion": "Selecciona una reclamación aprobada."})
        objeto.estado_caso = ObjetoPerdido.EstadoCaso.ENTREGADO
        objeto.fecha_devuelto = timezone.localdate()
        objeto.recuperador = objeto.reportado_por
        objeto.updated_by = request.user
        objeto.save()
        reclamacion.estado = Reclamacion.Estado.ENTREGADA
        reclamacion.revisada_por = request.user
        reclamacion.revisada_en = timezone.now()
        reclamacion.save(update_fields=("estado", "revisada_por", "revisada_en", "updated_at"))
        return Response(self.get_serializer(objeto).data)


class ReclamacionViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = ReclamacionSerializer
    permission_classes = (ObjetosPerdidosPermission,)
    http_method_names = ("get", "post", "head", "options")

    def get_queryset(self):
        user = self.request.user
        privada_ids = PrivadaMiembro.objects.filter(usuario=user, status="activo", deleted_at__isnull=True).values("privada_id")
        queryset = Reclamacion.objects.filter(status="activo", objeto__privada_id__in=privada_ids).select_related("objeto", "solicitante", "revisada_por").prefetch_related("respuestas__pregunta", "evidencias")
        if user.is_staff:
            queryset = Reclamacion.objects.filter(status="activo").select_related("objeto", "solicitante", "solicitante__perfil", "revisada_por").prefetch_related("respuestas__pregunta", "evidencias")
            objeto_id = self.request.query_params.get("objeto")
            return queryset.filter(objeto_id=objeto_id) if objeto_id else queryset
        moderadas = PrivadaMiembro.objects.filter(usuario=user, rol=RolPrivada.MODERADOR, status="activo", deleted_at__isnull=True).values("privada_id")
        queryset = queryset.select_related("solicitante__perfil").filter(Q(solicitante=user) | Q(objeto__reportado_por=user) | Q(objeto__responsable_resguardo=user) | Q(objeto__privada_id__in=moderadas)).distinct()
        objeto_id = self.request.query_params.get("objeto")
        return queryset.filter(objeto_id=objeto_id) if objeto_id else queryset

    def perform_create(self, serializer):
        objeto = serializer.validated_data["objeto"]
        if not es_miembro(self.request.user, objeto.privada_id) or objeto.reportado_por_id == self.request.user.id:
            raise PermissionDenied("No puedes reclamar este objeto.")
        reclamacion = serializer.save(solicitante=self.request.user, created_by=self.request.user, updated_by=self.request.user)
        objeto.estado_caso = ObjetoPerdido.EstadoCaso.RECLAMACION_EN_REVISION
        objeto.save(update_fields=("estado_caso", "updated_at"))

    @action(detail=True, methods=("post",), url_path="revisar")
    def revisar(self, request, pk=None):
        reclamacion = self.get_object()
        if reclamacion.objeto.reportado_por_id != request.user.id:
            raise PermissionDenied("Solo quien creó la publicación puede revisar esta reclamación.")
        nuevo = request.data.get("estado")
        permitidos = {Reclamacion.Estado.INFORMACION_REQUERIDA, Reclamacion.Estado.APROBADA, Reclamacion.Estado.RECHAZADA}
        if nuevo not in permitidos:
            raise ValidationError({"estado": "Resultado de revisión no válido."})
        notas = request.data.get("notas_revision", "").strip()
        if nuevo in {Reclamacion.Estado.INFORMACION_REQUERIDA, Reclamacion.Estado.RECHAZADA} and not notas:
            raise ValidationError({"notas_revision": "Escribe una explicación para el solicitante."})
        reclamacion.estado = nuevo
        reclamacion.notas_revision = notas
        reclamacion.revisada_por = request.user
        reclamacion.revisada_en = timezone.now()
        reclamacion.updated_by = request.user
        reclamacion.save()
        return Response(self.get_serializer(reclamacion).data)


class EntregaViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = EntregaSerializer
    permission_classes = (ObjetosPerdidosPermission,)
    http_method_names = ("get", "post", "head", "options")

    def get_queryset(self):
        user = self.request.user
        qs = EntregaObjeto.objects.filter(status="activo").select_related("objeto", "reclamacion", "entregado_por", "recibido_por", "autorizado_por")
        objeto_id = self.request.query_params.get("objeto")
        if user.is_staff:
            return qs.filter(objeto_id=objeto_id) if objeto_id else qs
        moderadas = PrivadaMiembro.objects.filter(usuario=user, rol=RolPrivada.MODERADOR, status="activo", deleted_at__isnull=True).values("privada_id")
        qs = qs.filter(Q(entregado_por=user) | Q(recibido_por=user) | Q(objeto__privada_id__in=moderadas)).distinct()
        return qs.filter(objeto_id=objeto_id) if objeto_id else qs

    def perform_create(self, serializer):
        objeto = serializer.validated_data["objeto"]
        if not (es_moderador(self.request.user, objeto.privada_id) or self.request.user.id in {objeto.reportado_por_id, objeto.responsable_resguardo_id, objeto.posible_localizador_id}):
            raise PermissionDenied("No puedes registrar esta entrega.")
        reclamacion = serializer.validated_data.get("reclamacion")
        if not es_miembro(serializer.validated_data["entregado_por"], objeto.privada_id) or not es_miembro(serializer.validated_data["recibido_por"], objeto.privada_id):
            raise ValidationError("Ambas personas deben ser miembros activos de la privada.")
        if objeto.tipo == ObjetoPerdido.Tipo.RESGUARDADO and (not reclamacion or reclamacion.estado != Reclamacion.Estado.APROBADA):
            raise ValidationError({"reclamacion": "Se requiere una reclamación aprobada."})
        serializer.save(autorizado_por=self.request.user, codigo_expira_en=timezone.now() + timedelta(hours=24), created_by=self.request.user, updated_by=self.request.user)

    @action(detail=True, methods=("post",), url_path="confirmar")
    def confirmar(self, request, pk=None):
        entrega = self.get_object()
        if entrega.codigo_usado_en:
            raise ValidationError("El código ya fue utilizado.")
        if request.data.get("codigo") != entrega.codigo_temporal or timezone.now() > entrega.codigo_expira_en:
            raise ValidationError({"codigo": "Código inválido o vencido."})
        if request.user.id == entrega.entregado_por_id:
            entrega.confirmacion_entrega = True
        elif request.user.id == entrega.recibido_por_id:
            entrega.confirmacion_recepcion = True
        elif es_moderador(request.user, entrega.objeto.privada_id):
            lado = request.data.get("lado")
            if lado == "entrega": entrega.confirmacion_entrega = True
            elif lado == "recepcion": entrega.confirmacion_recepcion = True
            else: raise ValidationError({"lado": "Indica entrega o recepcion."})
        else:
            raise PermissionDenied("No participas en esta entrega.")
        if entrega.confirmada:
            entrega.codigo_usado_en = timezone.now()
            entrega.objeto.estado_caso = ObjetoPerdido.EstadoCaso.RECUPERADO if entrega.objeto.tipo == ObjetoPerdido.Tipo.EXTRAVIADO else ObjetoPerdido.EstadoCaso.ENTREGADO
            entrega.objeto.fecha_devuelto = timezone.localdate()
            entrega.objeto.recuperador = entrega.entregado_por
            entrega.objeto.save()
            if entrega.reclamacion:
                entrega.reclamacion.estado = Reclamacion.Estado.ENTREGADA
                entrega.reclamacion.save(update_fields=("estado", "updated_at"))
        entrega.updated_by = request.user
        entrega.save()
        return Response(self.get_serializer(entrega).data, status=status.HTTP_200_OK)
