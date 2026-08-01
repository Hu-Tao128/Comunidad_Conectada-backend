from django.db import migrations
from django.utils import timezone


def reemplazar_modulo(apps, schema_editor):
    ModuloSistema = apps.get_model("communities", "ModuloSistema")
    Privada = apps.get_model("communities", "Privada")
    PrivadaModulo = apps.get_model("communities", "PrivadaModulo")

    encuestas = ModuloSistema.objects.filter(codigo="encuestas").first()
    if encuestas:
        encuestas.activo = False
        encuestas.status = "eliminado"
        encuestas.deleted_at = timezone.now()
        encuestas.save(update_fields=("activo", "status", "deleted_at"))
        PrivadaModulo.objects.filter(modulo_id=encuestas.pk).update(
            status="eliminado", deleted_at=timezone.now()
        )

    minutas, _ = ModuloSistema.objects.get_or_create(
        codigo="minutas",
        defaults={
            "nombre": "Minutas",
            "descripcion": "Acuerdos y seguimiento de reuniones de la privada.",
            "orden": 50,
            "activo": True,
        },
    )
    for privada in Privada.objects.filter(status="activo", deleted_at__isnull=True):
        PrivadaModulo.objects.get_or_create(
            privada_id=privada.pk,
            modulo_id=minutas.pk,
            defaults={"created_by_id": privada.creador_id},
        )


class Migration(migrations.Migration):
    dependencies = [("communities", "0006_privadamiembro_inactivated_at")]
    operations = [migrations.RunPython(reemplazar_modulo, migrations.RunPython.noop)]
