from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import Usuario
from apps.communities.models import Privada, PrivadaMiembro
from .models import EstadoReporte, Reporte


class ReporteApiTests(APITestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            username="habitante",
            email="habitante@example.com",
            password="password-seguro",
        )
        self.otro_usuario = Usuario.objects.create_user(
            username="otro",
            email="otro@example.com",
            password="password-seguro",
        )
        self.privada = Privada.objects.create(
            nombre="Privada de prueba",
            creador=self.usuario,
            created_by=self.usuario,
        )
        PrivadaMiembro.objects.create(
            privada=self.privada,
            usuario=self.usuario,
            created_by=self.usuario,
        )
        self.client.force_authenticate(self.usuario)

    def test_crea_reporte_asociado_al_usuario_autenticado(self):
        response = self.client.post(
            reverse("reporte-list"),
            {
                "privada": str(self.privada.id),
                "creador": str(self.otro_usuario.id),
                "titulo": "Lámpara dañada",
                "descripcion": "La lámpara del acceso no enciende.",
                "prioridad": "alta",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        reporte = Reporte.objects.get(id=response.data["id"])
        self.assertEqual(reporte.creador, self.usuario)
        self.assertEqual(reporte.num, 1)
        self.assertEqual(reporte.estado, EstadoReporte.PENDIENTE)

    def test_mis_reportes_y_conclusion_solo_una_vez(self):
        reporte = Reporte.objects.create(
            num=1,
            privada=self.privada,
            creador=self.usuario,
            titulo="Puerta averiada",
            descripcion="La puerta de acceso está atorada.",
            created_by=self.usuario,
        )

        response = self.client.get(reverse("reporte-mis-reportes"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

        url = reverse("reporte-concluir", args=[reporte.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["estado"], EstadoReporte.CONCLUIDO)

        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("estado", response.data)

    def test_actualiza_un_reporte_sin_cambiar_su_privada(self):
        reporte = Reporte.objects.create(
            num=1,
            privada=self.privada,
            creador=self.usuario,
            titulo="Puerta averiada",
            descripcion="La puerta de acceso está atorada.",
            created_by=self.usuario,
        )

        response = self.client.put(
            reverse("reporte-detail", args=[reporte.id]),
            {
                "titulo": "Puerta principal averiada",
                "descripcion": "La puerta principal del acceso está atorada.",
                "prioridad": "media",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        reporte.refresh_from_db()
        self.assertEqual(reporte.titulo, "Puerta principal averiada")
