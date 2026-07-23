from django.db import migrations


MODULOS = (
    ("usuarios", "Usuarios", 10),
    ("reportes", "Reportes", 20),
    ("reservaciones", "Reservaciones", 30),
    ("directorio", "Directorio", 40),
    ("encuestas", "Encuestas", 50),
    ("eventos", "Eventos", 60),
    ("objetos-perdidos", "Objetos perdidos", 70),
    ("pagos", "Pagos", 80),
)


def crear_catalogo_y_migrar_privadas(apps, schema_editor):
    ModuloSistema = apps.get_model("communities", "ModuloSistema")
    Privada = apps.get_model("communities", "Privada")
    PrivadaModulo = apps.get_model("communities", "PrivadaModulo")

    catalogo = []
    for codigo, nombre, orden in MODULOS:
        modulo, _ = ModuloSistema.objects.get_or_create(
            codigo=codigo,
            defaults={"nombre": nombre, "orden": orden, "activo": True},
        )
        catalogo.append(modulo)

    for privada in Privada.objects.all().iterator():
        PrivadaModulo.objects.bulk_create(
            [
                PrivadaModulo(
                    privada_id=privada.pk,
                    modulo_id=modulo.pk,
                    created_by_id=privada.creador_id,
                )
                for modulo in catalogo
            ],
            ignore_conflicts=True,
        )


class Migration(migrations.Migration):
    dependencies = [
        ("communities", "0004_modulosistema_privadamodulo"),
    ]

    operations = [
        migrations.RunPython(crear_catalogo_y_migrar_privadas, migrations.RunPython.noop),
    ]
