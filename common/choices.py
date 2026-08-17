from django.db import models

from .models import RecordStatus


class EstadoIncidente(models.TextChoices):
    PENDIENTE = "pendiente", "Pendiente"
    EN_PROCESO = "en_proceso", "En proceso"
    RESUELTO = "resuelto", "Resuelto"


class Prioridad(models.TextChoices):
    BAJA = "baja", "Baja"
    MEDIA = "media", "Media"
    ALTA = "alta", "Alta"


class EstadoPago(models.TextChoices):
    PENDIENTE = "pendiente", "Pendiente"
    EN_REVISION = "en_revision", "En revisión"
    PAGADO = "pagado", "Pagado"
    ATRASADO = "atrasado", "Atrasado"
    NO_PAGADO = "no_pagado", "No pagado"
    DECLINADO = "declinado", "Declinado"


class EstadoIntentoPago(models.TextChoices):
    EN_REVISION = "en_revision", "En revisión"
    ACEPTADO = "aceptado", "Aceptado"
    DECLINADO = "declinado", "Declinado"


class EstadoReservacion(models.TextChoices):
    PENDIENTE = "pendiente", "Pendiente"
    APROBADA = "aprobada", "Aprobada"
    CANCELADA = "cancelada", "Cancelada"

__all__ = (
    "RecordStatus",
    "EstadoIncidente",
    "Prioridad",
    "EstadoPago",
    "EstadoIntentoPago",
    "EstadoReservacion",
)
