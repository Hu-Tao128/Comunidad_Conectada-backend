from django.contrib import admin
from .models import Reservacion


@admin.register(Reservacion)
class ReservacionAdmin(admin.ModelAdmin):
    list_display = ("folio", "area", "usuario", "fecha", "hora_inicio", "estado", "status")
    search_fields = ("area__nombre", "usuario__username", "notas")
    list_filter = ("estado", "area", "status")
    ordering = ("fecha", "hora_inicio")
    readonly_fields = ("created_at", "updated_at", "deleted_at")
    autocomplete_fields = ("area", "usuario", "created_by", "updated_by")
