from django.contrib import admin

from .models import GaleriaImagen


class GaleriaDirectorioInline(admin.TabularInline):
    model = GaleriaImagen
    fk_name = "directorio"
    extra = 0
    fields = ("archivo", "orden", "status", "created_at")
    readonly_fields = ("created_at",)


class GaleriaEventoInline(admin.TabularInline):
    model = GaleriaImagen
    fk_name = "evento"
    extra = 0
    fields = ("archivo", "orden", "status", "created_at")
    readonly_fields = ("created_at",)


class GaleriaObjetoInline(admin.TabularInline):
    model = GaleriaImagen
    fk_name = "objeto"
    extra = 0
    fields = ("archivo", "orden", "status", "created_at")
    readonly_fields = ("created_at",)


@admin.register(GaleriaImagen)
class GaleriaImagenAdmin(admin.ModelAdmin):
    list_display = ("__str__", "archivo", "orden", "status", "created_at")
    list_filter = ("status",)
