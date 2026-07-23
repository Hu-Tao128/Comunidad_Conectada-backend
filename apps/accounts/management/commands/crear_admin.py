from django.core.management.base import BaseCommand

from apps.accounts.models import Usuario


class Command(BaseCommand):
    help = "Crea o actualiza un administrador global usando el hash de contraseñas de Django."

    def add_arguments(self, parser):
        parser.add_argument("--username", default="admin")
        parser.add_argument("--email", default="admin@comunidadconectada.local")
        parser.add_argument("--password", default="adminpassword")

    def handle(self, *args, **options):
        user, created = Usuario.objects.get_or_create(
            username=options["username"],
            defaults={"email": options["email"]},
        )
        user.email = options["email"]
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.set_password(options["password"])
        user.save()
        action = "creado" if created else "actualizado"
        self.stdout.write(self.style.SUCCESS(f"Administrador {action}: {user.username}"))
