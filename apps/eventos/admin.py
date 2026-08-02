from django.contrib import admin

from .models import Evento


@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ("titulo", "privada", "fecha_inicio", "fecha_fin", "status")
    list_filter = ("privada", "status")
    search_fields = ("titulo", "descripcion", "ubicacion")
