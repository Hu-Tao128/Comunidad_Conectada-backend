from rest_framework.permissions import IsAuthenticated, SAFE_METHODS


class ReservacionReadPermission(IsAuthenticated):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or request.method == "POST"
