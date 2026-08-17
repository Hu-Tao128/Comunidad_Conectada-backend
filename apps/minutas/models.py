from django.core.validators import MinLengthValidator
from django.db import models

from apps.accounts.models import Usuario
from apps.communities.models import Privada
from common.models import BaseModel


class TipoReunion(models.TextChoices):
    ORDINARIA = "ordinaria", "Ordinaria"
    EXTRAORDINARIA = "extraordinaria", "Extraordinaria"
    COMITE = "comite", "Comité"


class Minuta(BaseModel):
    privada = models.ForeignKey(Privada, on_delete=models.PROTECT, related_name="minutas")
    numero = models.PositiveIntegerField()
    titulo = models.CharField(max_length=180)
    tipo_reunion = models.CharField(max_length=20, choices=TipoReunion.choices, default=TipoReunion.ORDINARIA)
    fecha_reunion = models.DateTimeField()
    lugar = models.CharField(max_length=180)
    objetivo = models.TextField(validators=[MinLengthValidator(10)])
    asistentes = models.TextField(help_text="Un nombre por línea")
    orden_dia = models.TextField(validators=[MinLengthValidator(10)])
    acuerdos = models.TextField(validators=[MinLengthValidator(10)])
    compromisos = models.TextField(blank=True)
    observaciones = models.TextField(blank=True)
    proxima_reunion = models.DateTimeField(null=True, blank=True)
    moderador = models.ForeignKey(Usuario, on_delete=models.PROTECT, related_name="minutas_creadas")

    class Meta:
        ordering = ("-fecha_reunion", "-created_at")
        constraints = [models.UniqueConstraint(fields=("privada", "numero"), name="uq_minuta_numero_privada")]
        indexes = [models.Index(fields=("privada", "fecha_reunion"))]

    def __str__(self):
        return f"Minuta #{self.numero} - {self.titulo}"
