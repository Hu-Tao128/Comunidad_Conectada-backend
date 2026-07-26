"""Casos de uso de cuotas, comprobantes y validación de pagos."""

import cloudinary
import cloudinary.uploader
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.communities.models import PrivadaMiembro, RolPrivada
from common.choices import EstadoIntentoPago, EstadoPago
from .models import Cuota, Pago, PagoIntento


def configurar_cloudinary() -> None:
    if not all((settings.CLOUDINARY_CLOUD_NAME, settings.CLOUDINARY_API_KEY, settings.CLOUDINARY_API_SECRET)):
        raise ValidationError("Cloudinary no está configurado en el servidor.")
    cloudinary.config(
        cloud_name=settings.CLOUDINARY_CLOUD_NAME,
        api_key=settings.CLOUDINARY_API_KEY,
        api_secret=settings.CLOUDINARY_API_SECRET,
        secure=True,
    )


def subir_comprobante_cloudinary(archivo, pago: Pago) -> str:
    if getattr(archivo, "size", 0) > 8 * 1024 * 1024:
        raise ValidationError({"comprobante": "La imagen no puede superar 8 MB."})
    content_type = getattr(archivo, "content_type", "")
    if content_type not in {"image/jpeg", "image/png", "image/webp"}:
        raise ValidationError({"comprobante": "Solo se permiten imágenes JPG, PNG o WEBP."})
    configurar_cloudinary()
    resultado = cloudinary.uploader.upload(
        archivo,
        folder=f"comunidad_conectada/pagos/{pago.privada_id}/{pago.cuota_id}",
        resource_type="image",
        overwrite=False,
    )
    return resultado["secure_url"]


@transaction.atomic
def crear_cuota_con_pagos(*, datos: dict, moderador) -> Cuota:
    privada = datos["privada"]
    if not moderador.is_staff and not PrivadaMiembro.objects.filter(
        privada=privada,
        usuario=moderador,
        rol=RolPrivada.MODERADOR,
        status="activo",
        deleted_at__isnull=True,
    ).exists():
        raise ValidationError("Solo un moderador de la privada puede crear cuotas.")

    cuota = Cuota.objects.create(**datos, created_by=moderador)
    habitantes = PrivadaMiembro.objects.filter(
        privada=privada,
        rol=RolPrivada.HABITANTE,
        status="activo",
        deleted_at__isnull=True,
        usuario__is_active=True,
    ).select_related("usuario")
    Pago.objects.bulk_create([
        Pago(cuota=cuota, pagador=m.usuario, privada=privada, created_by=moderador)
        for m in habitantes
    ])
    return cuota


def crear_pagos_para_habitante(*, miembro) -> None:
    """Asigna las cuotas existentes cuando un habitante se incorpora a una privada."""
    cuotas = Cuota.objects.filter(
        privada=miembro.privada,
        status="activo",
        deleted_at__isnull=True,
    )
    Pago.objects.bulk_create(
        [
            Pago(
                cuota=cuota,
                pagador=miembro.usuario,
                privada=miembro.privada,
                created_by=miembro.usuario,
            )
            for cuota in cuotas
        ],
        ignore_conflicts=True,
    )


def actualizar_vencidos(queryset) -> None:
    queryset.filter(
        estado=EstadoPago.PENDIENTE,
        cuota__fecha_vencimiento__lt=timezone.localdate(),
    ).update(estado=EstadoPago.NO_PAGADO, updated_at=timezone.now())


@transaction.atomic
def registrar_comprobante(*, pago: Pago, archivo, usuario) -> PagoIntento:
    pago = Pago.objects.select_for_update().select_related("cuota").get(pk=pago.pk)
    if pago.pagador_id != usuario.id:
        raise ValidationError("Solo el pagador puede enviar este comprobante.")
    if pago.estado in {EstadoPago.PAGADO, EstadoPago.ATRASADO, EstadoPago.EN_REVISION}:
        raise ValidationError("Este pago no admite un nuevo comprobante en su estado actual.")

    url = subir_comprobante_cloudinary(archivo, pago)
    ahora = timezone.now()
    intento = PagoIntento.objects.create(
        pago=pago,
        comprobante_url=url,
        estado=EstadoIntentoPago.EN_REVISION,
        created_by=usuario,
    )
    pago.comprobante_url = url
    pago.fecha_pago = ahora
    pago.fecha_validacion = None
    pago.validador = None
    pago.estado = EstadoPago.EN_REVISION
    pago.updated_by = usuario
    pago.save(update_fields=("comprobante_url", "fecha_pago", "fecha_validacion", "validador", "estado", "updated_by", "updated_at"))
    return intento


@transaction.atomic
def validar_pago(*, pago: Pago, estado: str, moderador, motivo: str = "") -> Pago:
    pago = Pago.objects.select_for_update().select_related("cuota", "privada").get(pk=pago.pk)
    if not moderador.is_staff and not PrivadaMiembro.objects.filter(
        privada=pago.privada,
        usuario=moderador,
        rol=RolPrivada.MODERADOR,
        status="activo",
        deleted_at__isnull=True,
    ).exists():
        raise ValidationError("Solo un moderador de la privada puede validar este pago.")
    if pago.estado != EstadoPago.EN_REVISION:
        raise ValidationError("Solo se pueden validar pagos en revisión.")

    intento = pago.intentos.select_for_update().filter(estado=EstadoIntentoPago.EN_REVISION).first()
    if not intento:
        raise ValidationError("El pago no tiene un intento pendiente de revisión.")
    ahora = timezone.now()
    if estado == EstadoIntentoPago.ACEPTADO:
        pago.estado = EstadoPago.ATRASADO if timezone.localtime(pago.fecha_pago).date() > pago.cuota.fecha_vencimiento else EstadoPago.PAGADO
        intento.estado = EstadoIntentoPago.ACEPTADO
        intento.motivo_declinado = ""
    else:
        pago.estado = EstadoPago.DECLINADO
        intento.estado = EstadoIntentoPago.DECLINADO
        intento.motivo_declinado = motivo.strip()
    intento.validador = moderador
    intento.revisado_en = ahora
    intento.updated_by = moderador
    intento.save(update_fields=("estado", "motivo_declinado", "validador", "revisado_en", "updated_by", "updated_at"))
    pago.validador = moderador
    pago.fecha_validacion = ahora
    pago.updated_by = moderador
    pago.save(update_fields=("estado", "validador", "fecha_validacion", "updated_by", "updated_at"))
    return pago
