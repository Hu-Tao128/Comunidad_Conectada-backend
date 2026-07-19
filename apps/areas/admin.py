from django.contrib import admin
from .models import AreaComunitaria


@admin.register(AreaComunitaria)
class AreaComunitariaAdmin(admin.ModelAdmin):
    list_display = ("codigo", "nombre", "privada", "capacidad", "status")
    search_fields = ("nombre", "descripcion", "privada__nombre")
    list_filter = ("privada", "status")
    ordering = ("nombre",)
    readonly_fields = ("created_at", "updated_at", "deleted_at")
    autocomplete_fields = ("privada", "created_by", "updated_by")
