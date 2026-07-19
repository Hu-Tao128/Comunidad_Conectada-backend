from django.contrib import admin
from .models import Casa, Modulo, Privada


@admin.register(Privada)
class PrivadaAdmin(admin.ModelAdmin):
    list_display = ("codigo", "nombre", "creador", "status")
    search_fields = ("codigo", "nombre", "dir_ciudad")
    list_filter = ("status", "dir_estado")
    autocomplete_fields = ("creador", "created_by", "updated_by")


@admin.register(Modulo)
class ModuloAdmin(admin.ModelAdmin):
    list_display = ("nombre", "privada", "status")
    search_fields = ("nombre", "privada__nombre")
    list_filter = ("status", "privada")
    autocomplete_fields = ("privada", "created_by", "updated_by")


@admin.register(Casa)
class CasaAdmin(admin.ModelAdmin):
    list_display = ("numero", "modulo", "status")
    search_fields = ("numero", "modulo__nombre", "modulo__privada__nombre")
    list_filter = ("status", "modulo__privada")
    autocomplete_fields = ("modulo", "created_by", "updated_by")
