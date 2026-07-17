from django.contrib import admin
from .models import ObjetoPerdido


@admin.register(ObjetoPerdido)
class ObjetoPerdidoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "privada", "reportado_por", "tipo", "created_at")
    search_fields = ("nombre", "descripcion", "tipo", "reportado_por__username")
    list_filter = ("tipo", "privada", "status")
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at", "deleted_at")
    autocomplete_fields = ("privada", "reportado_por", "created_by", "updated_by")
