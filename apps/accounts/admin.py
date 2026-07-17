from django.contrib import admin
from .models import Perfil, Usuario


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "first_name", "last_name", "is_active", "is_staff")
    search_fields = ("username", "email", "first_name", "last_name")
    list_filter = ("is_active", "status", "is_staff", "groups")
    ordering = ("username",)
    readonly_fields = ("last_login", "date_joined")
    filter_horizontal = ("groups", "user_permissions")


@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ("usuario", "nombres", "apellidos", "casa", "telefono")
    search_fields = ("usuario__username", "usuario__email", "nombres", "apellidos", "telefono")
    autocomplete_fields = ("usuario", "casa")
