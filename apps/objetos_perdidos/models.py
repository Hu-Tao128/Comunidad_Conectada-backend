"""Objetos extraviados, resguardados, reclamaciones y entregas."""

import secrets

from django.db import models
from django.utils import timezone

from apps.accounts.models import Usuario
from apps.communities.models import Privada
from common.models import BaseModel


class ObjetoPerdido(BaseModel):
    class Tipo(models.TextChoices):
        EXTRAVIADO = "extraviado", "Objeto extraviado"
        RESGUARDADO = "resguardado", "Objeto resguardado"

    class EstadoCaso(models.TextChoices):
        ACTIVO = "activo", "Activo"
        POSIBLEMENTE_LOCALIZADO = "posiblemente_localizado", "Posiblemente localizado"
        RECLAMACION_EN_REVISION = "reclamacion_en_revision", "Reclamación en revisión"
        RECUPERADO = "recuperado", "Objeto recuperado"
        ENTREGADO = "entregado", "Entregado a su propietario"
        CERRADO = "cerrado", "Cerrado"

    privada = models.ForeignKey(
        Privada, on_delete=models.PROTECT, related_name="objetos_perdidos"
    )
    reportado_por = models.ForeignKey(
        Usuario, on_delete=models.PROTECT, related_name="objetos_reportados"
    )
    num = models.PositiveIntegerField(unique=True)
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField()
    tipo = models.CharField(
        max_length=15, choices=Tipo.choices, default=Tipo.EXTRAVIADO
    )
    estado_caso = models.CharField(
        max_length=32,
        choices=EstadoCaso.choices,
        default=EstadoCaso.ACTIVO,
        db_index=True,
    )
    imagen = models.ImageField(
        upload_to="objetos_perdidos/", blank=True, max_length=500
    )
    ubicacion = models.CharField(max_length=250, blank=True)
    fecha_evento = models.DateTimeField(null=True, blank=True)
    informacion_adicional = models.TextField(blank=True)
    detalles_privados = models.TextField(blank=True)
    responsable_resguardo = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        related_name="objetos_resguardados",
        null=True,
        blank=True,
    )
    posible_localizador = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        related_name="objetos_posiblemente_localizados",
        null=True,
        blank=True,
    )
    fecha_reporte = models.DateField(
        null=True, blank=True
    )  # Compatibilidad con clientes anteriores.
    fecha_encontrado = models.DateField(null=True, blank=True)
    fecha_devuelto = models.DateField(null=True, blank=True)
    recuperador = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        related_name="objetos_recuperados",
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ("-created_at",)
        indexes = [models.Index(fields=("privada", "tipo", "estado_caso"))]

    @property
    def finalizado(self):
        return self.estado_caso in {
            self.EstadoCaso.RECUPERADO,
            self.EstadoCaso.ENTREGADO,
            self.EstadoCaso.CERRADO,
        }

    def __str__(self):
        return self.nombre


class PreguntaValidacion(BaseModel):
    objeto = models.ForeignKey(
        ObjetoPerdido, on_delete=models.CASCADE, related_name="preguntas_validacion"
    )
    pregunta = models.CharField(max_length=300)
    orden = models.PositiveSmallIntegerField(default=1)

    class Meta:
        ordering = ("orden", "created_at")
        constraints = [
            models.UniqueConstraint(
                fields=("objeto", "orden"), name="uq_pregunta_objeto_orden"
            )
        ]


class Reclamacion(BaseModel):
    class Estado(models.TextChoices):
        PENDIENTE = "pendiente", "Pendiente de revisión"
        INFORMACION_REQUERIDA = (
            "informacion_requerida",
            "Información adicional requerida",
        )
        APROBADA = "aprobada", "Reclamación aprobada"
        RECHAZADA = "rechazada", "Reclamación rechazada"
        ENTREGADA = "entregada", "Objeto entregado"

    objeto = models.ForeignKey(
        ObjetoPerdido, on_delete=models.PROTECT, related_name="reclamaciones"
    )
    solicitante = models.ForeignKey(
        Usuario, on_delete=models.PROTECT, related_name="reclamaciones_objetos"
    )
    estado = models.CharField(
        max_length=24, choices=Estado.choices, default=Estado.PENDIENTE, db_index=True
    )
    mensaje = models.TextField(blank=True)
    notas_revision = models.TextField(blank=True)
    revisada_por = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        related_name="reclamaciones_revisadas",
        null=True,
        blank=True,
    )
    revisada_en = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-created_at",)
        constraints = [
            models.UniqueConstraint(
                fields=("objeto", "solicitante"),
                condition=models.Q(status="activo"),
                name="uq_reclamacion_activa_objeto_usuario",
            )
        ]


class RespuestaValidacion(BaseModel):
    reclamacion = models.ForeignKey(
        Reclamacion, on_delete=models.CASCADE, related_name="respuestas"
    )
    pregunta = models.ForeignKey(
        PreguntaValidacion, on_delete=models.PROTECT, related_name="respuestas"
    )
    respuesta = models.TextField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("reclamacion", "pregunta"),
                name="uq_respuesta_reclamacion_pregunta",
            )
        ]


class EvidenciaPropiedad(BaseModel):
    reclamacion = models.ForeignKey(
        Reclamacion, on_delete=models.CASCADE, related_name="evidencias"
    )
    archivo = models.FileField(upload_to="objetos_perdidos/evidencias/", max_length=500)
    descripcion = models.CharField(max_length=250, blank=True)


def generar_codigo_entrega():
    return f"{secrets.randbelow(1_000_000):06d}"


class EntregaObjeto(BaseModel):
    objeto = models.OneToOneField(
        ObjetoPerdido, on_delete=models.PROTECT, related_name="entrega"
    )
    reclamacion = models.OneToOneField(
        Reclamacion,
        on_delete=models.PROTECT,
        related_name="entrega",
        null=True,
        blank=True,
    )
    entregado_por = models.ForeignKey(
        Usuario, on_delete=models.PROTECT, related_name="entregas_realizadas"
    )
    recibido_por = models.ForeignKey(
        Usuario, on_delete=models.PROTECT, related_name="entregas_recibidas"
    )
    autorizado_por = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        related_name="entregas_autorizadas",
        null=True,
        blank=True,
    )
    resultado = models.TextField(blank=True)
    fecha_entrega = models.DateTimeField(default=timezone.now)
    confirmacion_entrega = models.BooleanField(default=False)
    confirmacion_recepcion = models.BooleanField(default=False)
    codigo_temporal = models.CharField(max_length=6, default=generar_codigo_entrega)
    codigo_expira_en = models.DateTimeField()
    codigo_usado_en = models.DateTimeField(null=True, blank=True)

    @property
    def confirmada(self):
        return self.confirmacion_entrega and self.confirmacion_recepcion
