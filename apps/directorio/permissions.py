from rest_framework.permissions import IsAuthenticated


class DirectorioReadPermission(IsAuthenticated):
    pass
