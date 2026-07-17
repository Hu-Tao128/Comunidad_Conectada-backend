from django.contrib import admin
from .models import Directorio


@admin.register(Directorio)
class DirectorioAdmin(admin.ModelAdmin):
    list_display = ("nombre", "categorias", "privada", "num_tel", "status")
    search_fields = ("nombre", "categorias", "num_tel", "codigo")
    list_filter = ("categorias", "status", "privada")
    ordering = ("nombre",)
    readonly_fields = ("created_at", "updated_at", "deleted_at")
    autocomplete_fields = ("privada", "created_by", "updated_by")
