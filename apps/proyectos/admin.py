from django.contrib import admin
from .models import Proyecto


@admin.register(Proyecto)
class ProyectoAdmin(admin.ModelAdmin):
    list_display = ("codigo", "nombre", "privada", "estado", "status")
    search_fields = ("nombre", "descripcion", "privada__nombre")
    list_filter = ("estado", "privada", "status")
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at", "deleted_at")
    autocomplete_fields = ("privada", "created_by", "updated_by")
