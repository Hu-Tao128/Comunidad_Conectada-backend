import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("pagos", "0002_alter_pago_estado"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(model_name="cuota", name="tipo_pago", field=models.CharField(choices=[("mensual", "Mensual"), ("unico", "Único")], default="unico", max_length=20)),
        migrations.AddField(model_name="cuota", name="icono", field=models.CharField(blank=True, max_length=50)),
        migrations.AddField(model_name="cuota", name="color_icono", field=models.CharField(blank=True, max_length=30)),
        migrations.RemoveField(model_name="pago", name="monto"),
        migrations.RemoveField(model_name="pago", name="num"),
        migrations.RemoveField(model_name="pago", name="pagado_en"),
        migrations.RenameField(model_name="pago", old_name="comprobante", new_name="comprobante_url"),
        migrations.AlterField(model_name="pago", name="comprobante_url", field=models.URLField(blank=True, max_length=500)),
        migrations.AlterField(model_name="pago", name="estado", field=models.CharField(choices=[("pendiente", "Pendiente"), ("en_revision", "En revisión"), ("pagado", "Pagado"), ("atrasado", "Atrasado"), ("no_pagado", "No pagado"), ("declinado", "Declinado")], db_index=True, default="pendiente", max_length=20)),
        migrations.AddConstraint(model_name="pago", constraint=models.UniqueConstraint(fields=("cuota", "pagador"), name="uq_pago_cuota_pagador")),
        migrations.CreateModel(
            name="PagoIntento",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("status", models.CharField(choices=[("activo", "Activo"), ("suspendido", "Suspendido"), ("eliminado", "Eliminado")], db_index=True, default="activo", max_length=12)),
                ("deleted_at", models.DateTimeField(blank=True, db_index=True, null=True)),
                ("created_ip", models.GenericIPAddressField(blank=True, null=True)),
                ("updated_ip", models.GenericIPAddressField(blank=True, null=True)),
                ("comprobante_url", models.URLField(max_length=500)),
                ("estado", models.CharField(choices=[("en_revision", "En revisión"), ("aceptado", "Aceptado"), ("declinado", "Declinado")], db_index=True, default="en_revision", max_length=20)),
                ("enviado_en", models.DateTimeField(auto_now_add=True)),
                ("revisado_en", models.DateTimeField(blank=True, null=True)),
                ("motivo_declinado", models.TextField(blank=True)),
                ("created_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="%(app_label)s_%(class)s_created", to=settings.AUTH_USER_MODEL)),
                ("updated_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="%(app_label)s_%(class)s_updated", to=settings.AUTH_USER_MODEL)),
                ("pago", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="intentos", to="pagos.pago")),
                ("validador", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="intentos_pago_validados", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ("-enviado_en",)},
        ),
        migrations.AddIndex(model_name="pagointento", index=models.Index(fields=["pago", "estado"], name="pagos_pagoi_pago_id_4e0b40_idx")),
    ]
