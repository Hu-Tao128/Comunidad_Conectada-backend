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
    PAGADO = "pagado", "Pagado"
    ATRASADO = "atrasado", "Atrasado"
    NO_PAGADO = "no_pagado", "No pagado"


class EstadoReservacion(models.TextChoices):
    PENDIENTE = "pendiente", "Pendiente"
    APROBADA = "aprobada", "Aprobada"
    CANCELADA = "cancelada", "Cancelada"

__all__ = (
    "RecordStatus",
    "EstadoIncidente",
    "Prioridad",
    "EstadoPago",
    "EstadoReservacion",
)
