from django.contrib import admin

from .models import Minuta


@admin.register(Minuta)
class MinutaAdmin(admin.ModelAdmin):
    list_display = ("numero", "titulo", "privada", "tipo_reunion", "fecha_reunion", "moderador")
    list_filter = ("tipo_reunion", "privada")
    search_fields = ("titulo", "objetivo", "acuerdos")
