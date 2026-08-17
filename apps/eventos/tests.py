from datetime import date, time, timedelta

from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import Usuario
from apps.areas.models import AreaComunitaria
from apps.communities.models import Privada, PrivadaMiembro, RolPrivada
from apps.reservas.models import Reservacion


class ModulosRDEApiTests(APITestCase):
    def setUp(self):
        self.moderador = Usuario.objects.create_user(username="moderador", email="moderador@example.com", password="secret")
        self.habitante = Usuario.objects.create_user(username="habitante", email="habitante@example.com", password="secret")
        self.privada = Privada.objects.create(nombre="Las Flores", creador=self.moderador)
        PrivadaMiembro.objects.create(privada=self.privada, usuario=self.moderador, rol=RolPrivada.MODERADOR)
        PrivadaMiembro.objects.create(privada=self.privada, usuario=self.habitante, rol=RolPrivada.HABITANTE)
        self.area = AreaComunitaria.objects.create(privada=self.privada, codigo="SALON-01", nombre="Salón", capacidad=50)

    def test_moderador_puede_crear_evento(self):
        self.client.force_authenticate(self.moderador)
        response = self.client.post("/api/eventos/", {
            "privada": str(self.privada.id),
            "titulo": "Asamblea vecinal",
            "fecha_inicio": (timezone.now() + timedelta(days=1)).isoformat(),
            "ubicacion": "Casa club",
        }, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["titulo"], "Asamblea vecinal")

    def test_habitante_no_puede_crear_directorio(self):
        self.client.force_authenticate(self.habitante)
        response = self.client.post("/api/directorio/", {
            "privada": str(self.privada.id),
            "nombre": "Plomería local",
            "categorias": "hogar",
        }, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_reservacion_solapada_es_rechazada(self):
        Reservacion.objects.create(
            folio=1,
            area=self.area,
            usuario=self.habitante,
            fecha=date.today(),
            hora_inicio=time(10, 0),
            hora_fin=time(12, 0),
        )
        self.client.force_authenticate(self.habitante)
        response = self.client.post("/api/reservaciones/", {
            "area": str(self.area.id),
            "fecha": date.today().isoformat(),
            "hora_inicio": "11:00:00",
            "hora_fin": "13:00:00",
            "num_asistentes": 4,
        }, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
