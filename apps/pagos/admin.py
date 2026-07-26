from django.contrib import admin
from .models import Cuota, Pago, PagoIntento


@admin.register(Cuota)
class CuotaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "privada", "monto", "fecha_vencimiento", "status")
    search_fields = ("nombre", "clave", "privada__nombre")
    list_filter = ("privada", "fecha_vencimiento", "status")
    ordering = ("-fecha_vencimiento",)
    readonly_fields = ("created_at", "updated_at", "deleted_at")
    autocomplete_fields = ("privada", "created_by", "updated_by")


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ("cuota", "pagador", "estado", "fecha_pago", "created_at")
    search_fields = ("pagador__username", "pagador__email", "cuota__nombre")
    list_filter = ("estado", "status")
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at", "deleted_at")
    autocomplete_fields = ("cuota", "pagador", "privada", "validador", "created_by", "updated_by")


@admin.register(PagoIntento)
class PagoIntentoAdmin(admin.ModelAdmin):
    list_display = ("pago", "estado", "enviado_en", "revisado_en", "validador")
    search_fields = ("pago__pagador__username", "pago__cuota__nombre")
    list_filter = ("estado",)
    readonly_fields = ("created_at", "updated_at", "enviado_en")
