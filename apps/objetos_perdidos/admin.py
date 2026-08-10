from django.contrib import admin

from .models import EntregaObjeto, EvidenciaPropiedad, ObjetoPerdido, PreguntaValidacion, Reclamacion, RespuestaValidacion


class PreguntaInline(admin.TabularInline):
    model = PreguntaValidacion
    extra = 0


@admin.register(ObjetoPerdido)
class ObjetoPerdidoAdmin(admin.ModelAdmin):
    list_display = ("num", "nombre", "privada", "reportado_por", "tipo", "estado_caso", "created_at")
    search_fields = ("nombre", "descripcion", "ubicacion", "reportado_por__username")
    list_filter = ("tipo", "estado_caso", "privada", "status")
    inlines = (PreguntaInline,)


admin.site.register(Reclamacion)
admin.site.register(RespuestaValidacion)
admin.site.register(EvidenciaPropiedad)
admin.site.register(EntregaObjeto)
