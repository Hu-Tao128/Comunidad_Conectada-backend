from django.contrib import admin
from .models import Incidente, Reporte


@admin.register(Reporte)
class ReporteAdmin(admin.ModelAdmin):
    list_display = ("num", "titulo", "privada", "creador", "estado", "created_at")
    search_fields = ("titulo", "descripcion", "creador__username")
    list_filter = ("estado", "privada", "status")
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at", "deleted_at")
    autocomplete_fields = ("privada", "creador", "supervisor", "created_by", "updated_by")


@admin.register(Incidente)
class IncidenteAdmin(admin.ModelAdmin):
    list_display = ("reporte", "tipo", "ubicacion", "created_at")
    search_fields = ("reporte__titulo", "ubicacion")
    list_filter = ("tipo", "status")
    readonly_fields = ("created_at", "updated_at", "deleted_at")
    autocomplete_fields = ("reporte", "usuario", "privada", "created_by", "updated_by")
