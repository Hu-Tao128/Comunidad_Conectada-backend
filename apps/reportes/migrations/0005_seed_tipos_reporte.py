from django.db import migrations


def crear_tipos(apps, schema_editor):
    TipoReporte = apps.get_model("reportes", "TipoReporte")
    for codigo, nombre in (
        ("seguridad", "Seguridad"),
        ("convivencia", "Convivencia"),
        ("mantenimiento", "Mantenimiento"),
    ):
        TipoReporte.objects.get_or_create(codigo=codigo, defaults={"nombre": nombre})


class Migration(migrations.Migration):
    dependencies = [("reportes", "0004_incidente_descripcion_incidente_titulo_and_more")]
    operations = [migrations.RunPython(crear_tipos, migrations.RunPython.noop)]
