from rest_framework.permissions import IsAuthenticated


class ReservacionReadPermission(IsAuthenticated):
    pass
