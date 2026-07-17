"""Reservaciones de áreas comunitarias."""

from django.core.exceptions import ValidationError
from django.db import models

from apps.accounts.models import Usuario
from apps.areas.models import AreaComunitaria
from common.models import BaseModel


class Reservacion(BaseModel):
    """Reserva de un área por un usuario."""

    class Estado(models.TextChoices):
        PENDIENTE = "pendiente", "Pendiente"
        CONFIRMADA = "confirmada", "Confirmada"
        CANCELADA = "cancelada", "Cancelada"

    folio = models.PositiveIntegerField(unique=True)
    area = models.ForeignKey(AreaComunitaria, on_delete=models.PROTECT, related_name="reservaciones")
    usuario = models.ForeignKey(Usuario, on_delete=models.PROTECT, related_name="reservaciones")
    fecha = models.DateField(db_index=True)
    hora_inicio = models.TimeField(db_index=True)
    hora_fin = models.TimeField(db_index=True)
    num_asistentes = models.PositiveIntegerField(default=1)
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.PENDIENTE, db_index=True)
    descripcion = models.TextField(blank=True)

    class Meta:
        verbose_name = "reservación"
        verbose_name_plural = "reservaciones"
        ordering = ("fecha", "hora_inicio")
        indexes = [models.Index(fields=("area", "fecha", "hora_inicio"))]

    def clean(self) -> None:
        if self.hora_fin <= self.hora_inicio:
            raise ValidationError({"hora_fin": "La hora final debe ser posterior a la inicial."})

    def __str__(self) -> str:
        return f"{self.area} - {self.fecha} {self.hora_inicio}"
