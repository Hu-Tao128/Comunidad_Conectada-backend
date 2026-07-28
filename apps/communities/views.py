from django.db import transaction
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
import cloudinary
import cloudinary.uploader
from rest_framework import generics, status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from common.mixins import PrivateScopedViewSet, ReadOnlyViewSet
from .models import (
    Casa,
    Modulo,
    ModuloSistema,
    Privada,
    PrivadaMiembro,
    PrivadaModulo,
    RolPrivada,
)
from .serializers import (
    CasaSerializer,
    CrearPrivadaSerializer,
    ModuloSerializer,
    ModuloSistemaSerializer,
    PrivadaAdminSerializer,
    AdminPrivadaModulosSerializer,
    AgregarMiembroSerializer,
    EditarMiembroSerializer,
    PrivadaMiembroSerializer,
    PrivadaSerializer,
    UnirsePrivadaSerializer,
)


class PrivadaViewSet(PrivateScopedViewSet):
    private_lookup = "id"
    queryset = Privada.objects.select_related("creador").filter(
        status="activo", deleted_at__isnull=True
    )
    serializer_class = PrivadaSerializer
    search_fields = ("codigo", "nombre", "dir_ciudad")
    ordering_fields = ("nombre", "codigo")


class ModuloViewSet(PrivateScopedViewSet):
    queryset = Modulo.objects.select_related("privada").filter(
        status="activo", deleted_at__isnull=True
    )
    serializer_class = ModuloSerializer
    search_fields = ("nombre", "privada__nombre")
    ordering_fields = ("nombre",)


class CasaViewSet(PrivateScopedViewSet):
    private_lookup = "modulo__privada_id"
    queryset = Casa.objects.select_related("modulo", "modulo__privada").filter(
        status="activo", deleted_at__isnull=True
    )
    serializer_class = CasaSerializer
    search_fields = ("numero", "modulo__nombre")
    ordering_fields = ("numero",)


class ModuloSistemaViewSet(ReadOnlyViewSet):
    queryset = ModuloSistema.objects.filter(
        activo=True, status="activo", deleted_at__isnull=True
    )
    serializer_class = ModuloSistemaSerializer
    pagination_class = None
    search_fields = ("codigo", "nombre")
    ordering_fields = ("orden", "nombre")


class AdminPrivadasView(generics.ListAPIView):
    serializer_class = PrivadaAdminSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = None

    def get_queryset(self):
        if not self.request.user.is_staff:
            raise PermissionDenied(
                "Solo el administrador de Comunidad Conectada puede consultar este recurso."
            )
        return Privada.objects.select_related("creador").filter(
            status="activo", deleted_at__isnull=True
        )


class AdminModulosView(generics.ListCreateAPIView):
    serializer_class = ModuloSistemaSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = None

    def get_queryset(self):
        if not self.request.user.is_staff:
            raise PermissionDenied(
                "Solo el administrador de Comunidad Conectada puede administrar módulos."
            )
        return ModuloSistema.objects.all()

    def perform_create(self, serializer):
        if not self.request.user.is_staff:
            raise PermissionDenied(
                "Solo el administrador de Comunidad Conectada puede administrar módulos."
            )
        serializer.save(created_by=self.request.user)


class AdminPrivadaModulosView(APIView):
    permission_classes = (IsAuthenticated,)

    @transaction.atomic
    def patch(self, request, privada_id):
        if not request.user.is_staff:
            raise PermissionDenied(
                "Solo el administrador puede modificar los módulos de una privada."
            )
        try:
            privada = Privada.objects.get(
                id=privada_id, status="activo", deleted_at__isnull=True
            )
        except Privada.DoesNotExist:
            raise ValidationError("La privada no existe.")

        serializer = AdminPrivadaModulosSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        codes = serializer.validated_data["modulos_contratados"]
        PrivadaModulo.objects.filter(privada=privada).update(
            status="eliminado", deleted_at=timezone.now(), updated_by=request.user
        )
        PrivadaModulo.objects.bulk_create(
            [
                PrivadaModulo(privada=privada, modulo=modulo, created_by=request.user)
                for modulo in ModuloSistema.objects.filter(
                    codigo__in=codes, activo=True
                )
            ]
        )
        return Response(PrivadaAdminSerializer(privada).data)


class MisPrivadasView(generics.ListAPIView):
    serializer_class = PrivadaMiembroSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = None

    def get_queryset(self):
        return PrivadaMiembro.all_objects.filter(
            usuario=self.request.user,
            status__in=("activo", "suspendido"),
            deleted_at__isnull=True,
            privada__status="activo",
            privada__deleted_at__isnull=True,
        ).select_related("privada", "usuario")


class CrearPrivadaView(APIView):
    permission_classes = (IsAuthenticated,)

    @transaction.atomic
    def post(self, request):
        serializer = CrearPrivadaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        nombres_modulos = serializer.validated_data.pop("modulos", [])
        codigos_contratados = serializer.validated_data.pop("modulos_contratados", [])
        privada = serializer.save(creador=request.user, created_by=request.user)
        Modulo.objects.bulk_create(
            [
                Modulo(
                    privada=privada,
                    nombre=nombre,
                    created_by=request.user,
                )
                for nombre in nombres_modulos
            ]
        )
        ModuloSistema.objects.filter(
            codigo__in=codigos_contratados, activo=True
        ).update(updated_by=request.user)
        PrivadaModulo.objects.bulk_create(
            [
                PrivadaModulo(privada=privada, modulo=modulo, created_by=request.user)
                for modulo in ModuloSistema.objects.filter(
                    codigo__in=codigos_contratados, activo=True
                )
            ]
        )
        miembro = PrivadaMiembro.objects.create(
            privada=privada,
            usuario=request.user,
            rol=RolPrivada.MODERADOR,
            created_by=request.user,
        )
        return Response(
            {
                "privada": PrivadaSerializer(privada).data,
                "membresia": PrivadaMiembroSerializer(miembro).data,
            },
            status=status.HTTP_201_CREATED,
        )


class UnirsePrivadaView(APIView):
    permission_classes = (IsAuthenticated,)

    @transaction.atomic
    def post(self, request):
        serializer = UnirsePrivadaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            privada = Privada.objects.get(
                codigo__iexact=serializer.validated_data["codigo"],
                status="activo",
                deleted_at__isnull=True,
            )
        except Privada.DoesNotExist:
            raise ValidationError({"codigo": "No existe una privada con ese código."})

        if PrivadaMiembro.objects.filter(
            usuario=request.user, privada=privada, status="activo"
        ).exists():
            raise ValidationError({"codigo": "Ya perteneces a esta privada."})

        miembro = PrivadaMiembro.objects.create(
            privada=privada,
            usuario=request.user,
            rol=RolPrivada.HABITANTE,
            created_by=request.user,
        )
        from apps.pagos.services import crear_pagos_para_habitante

        crear_pagos_para_habitante(miembro=miembro)
        return Response(
            {
                "privada": PrivadaSerializer(privada).data,
                "membresia": PrivadaMiembroSerializer(miembro).data,
            },
            status=status.HTTP_201_CREATED,
        )


class PromoverModeradorView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, privada_id, usuario_id):
        if (
            not request.user.is_staff
            and not PrivadaMiembro.objects.filter(
                privada_id=privada_id,
                usuario=request.user,
                rol=RolPrivada.MODERADOR,
                status="activo",
                deleted_at__isnull=True,
            ).exists()
        ):
            raise PermissionDenied("Solo un moderador puede asignar moderadores.")

        try:
            miembro = PrivadaMiembro.objects.select_related("privada", "usuario").get(
                privada_id=privada_id,
                usuario_id=usuario_id,
                status="activo",
                deleted_at__isnull=True,
            )
        except PrivadaMiembro.DoesNotExist:
            raise ValidationError("El usuario no pertenece a esta privada.")

        miembro.rol = RolPrivada.MODERADOR
        miembro.updated_by = request.user
        miembro.save(update_fields=("rol", "updated_by", "updated_at"))
        return Response(PrivadaMiembroSerializer(miembro).data)


def _exigir_moderador(request, privada_id):
    if request.user.is_staff:
        return
    if not PrivadaMiembro.objects.filter(
        privada_id=privada_id, usuario=request.user, rol=RolPrivada.MODERADOR,
        status="activo", deleted_at__isnull=True,
    ).exists():
        raise PermissionDenied("Solo un moderador activo puede gestionar usuarios de esta privada.")


class MiembrosPrivadaView(APIView):
    permission_classes = (IsAuthenticated,)

    @transaction.atomic
    def post(self, request, privada_id):
        _exigir_moderador(request, privada_id)
        serializer = AgregarMiembroSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        User = get_user_model()
        try:
            usuario = User.objects.get(
                email__iexact=serializer.validated_data["email"].strip(),
                is_active=True,
                status="activo",
            )
        except User.DoesNotExist:
            raise ValidationError({"email": "No existe una cuenta activa con ese correo electrónico."})

        miembro, creado = PrivadaMiembro.all_objects.get_or_create(
            privada_id=privada_id,
            usuario=usuario,
            defaults={
                "rol": serializer.validated_data["rol"],
                "created_by": request.user,
            },
        )
        if not creado and miembro.status == "activo" and miembro.deleted_at is None:
            raise ValidationError({"email": "Este usuario ya pertenece a la privada."})
        if not creado:
            miembro.status = "activo"
            miembro.deleted_at = None
            miembro.inactivated_at = None
            miembro.rol = serializer.validated_data["rol"]
            miembro.updated_by = request.user
            miembro.save(update_fields=("status", "deleted_at", "inactivated_at", "rol", "updated_by", "updated_at"))

        if miembro.rol == RolPrivada.HABITANTE:
            from apps.pagos.services import crear_pagos_para_habitante
            crear_pagos_para_habitante(miembro=miembro)
        return Response(PrivadaMiembroSerializer(miembro).data, status=status.HTTP_201_CREATED)


class AdministrarMiembroView(APIView):
    permission_classes = (IsAuthenticated,)

    def _miembro(self, privada_id, usuario_id):
        try:
            return PrivadaMiembro.all_objects.select_related("usuario", "privada").get(
                privada_id=privada_id, usuario_id=usuario_id, deleted_at__isnull=True
            )
        except PrivadaMiembro.DoesNotExist:
            raise ValidationError("El usuario no pertenece a esta privada.")

    @transaction.atomic
    def patch(self, request, privada_id, usuario_id):
        _exigir_moderador(request, privada_id)
        miembro = self._miembro(privada_id, usuario_id)
        if miembro.usuario_id == request.user.id:
            raise PermissionDenied("No puedes editar tu propia membresía desde Gestión de Usuarios.")
        serializer = EditarMiembroSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        nuevo_rol = serializer.validated_data["rol"]
        nuevo_estado = serializer.validated_data["status"]

        pierde_moderador = miembro.rol == RolPrivada.MODERADOR and (
            nuevo_rol != RolPrivada.MODERADOR or nuevo_estado != "activo"
        )
        if pierde_moderador and not PrivadaMiembro.objects.filter(
            privada_id=privada_id, rol=RolPrivada.MODERADOR, status="activo",
            deleted_at__isnull=True,
        ).exclude(pk=miembro.pk).exists():
            raise ValidationError("La privada debe conservar al menos un moderador activo.")

        miembro.rol = nuevo_rol
        miembro.status = nuevo_estado
        miembro.inactivated_at = timezone.now() if nuevo_estado == "suspendido" else None
        miembro.updated_by = request.user
        miembro.save(update_fields=("rol", "status", "inactivated_at", "updated_by", "updated_at"))
        if nuevo_estado == "activo" and nuevo_rol == RolPrivada.HABITANTE:
            from apps.pagos.services import crear_pagos_para_habitante
            crear_pagos_para_habitante(miembro=miembro)
        return Response(PrivadaMiembroSerializer(miembro).data)

    def post(self, request, privada_id, usuario_id):
        """Actualiza la foto de perfil del usuario mediante Cloudinary."""
        _exigir_moderador(request, privada_id)
        miembro = self._miembro(privada_id, usuario_id)
        if miembro.usuario_id == request.user.id:
            raise PermissionDenied("No puedes editar tu propia información desde Gestión de Usuarios.")
        archivo = request.FILES.get("avatar")
        if not archivo:
            raise ValidationError({"avatar": "Selecciona una imagen."})
        if archivo.size > 8 * 1024 * 1024 or archivo.content_type not in {"image/jpeg", "image/png", "image/webp"}:
            raise ValidationError({"avatar": "Usa una imagen JPG, PNG o WEBP de máximo 8 MB."})
        if not all((settings.CLOUDINARY_CLOUD_NAME, settings.CLOUDINARY_API_KEY, settings.CLOUDINARY_API_SECRET)):
            raise ValidationError({"avatar": "Cloudinary no está configurado en el servidor."})
        cloudinary.config(cloud_name=settings.CLOUDINARY_CLOUD_NAME, api_key=settings.CLOUDINARY_API_KEY,
                          api_secret=settings.CLOUDINARY_API_SECRET, secure=True)
        resultado = cloudinary.uploader.upload(
            archivo, folder=f"comunidad_conectada/perfiles/{privada_id}", resource_type="image", overwrite=False
        )
        from apps.accounts.models import Perfil
        perfil, _ = Perfil.objects.get_or_create(usuario=miembro.usuario)
        perfil.avatar = resultado["secure_url"]
        perfil.save(update_fields=("avatar",))
        return Response({"avatar": perfil.avatar})
