from django.contrib import admin
from .models import Cuota, Pago


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
    list_display = ("num", "cuota", "pagador", "monto", "estado", "created_at")
    search_fields = ("num", "pagador__username", "cuota__nombre")
    list_filter = ("estado", "status")
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at", "deleted_at")
    autocomplete_fields = ("cuota", "pagador", "privada", "validador", "created_by", "updated_by")
