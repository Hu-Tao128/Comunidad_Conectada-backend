from django.db import migrations


def asignar_creadores_como_moderadores(apps, schema_editor):
    Privada = apps.get_model("communities", "Privada")
    PrivadaMiembro = apps.get_model("communities", "PrivadaMiembro")

    for privada in Privada.objects.all().iterator():
        PrivadaMiembro.objects.get_or_create(
            privada_id=privada.pk,
            usuario_id=privada.creador_id,
            defaults={
                "rol": "moderador",
                "created_by_id": privada.creador_id,
            },
        )


class Migration(migrations.Migration):
    dependencies = [
        ("communities", "0002_alter_privada_codigo_privadamiembro"),
    ]

    operations = [
        migrations.RunPython(asignar_creadores_como_moderadores, migrations.RunPython.noop),
    ]
