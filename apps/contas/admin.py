from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Usuario

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ("username", "get_full_name", "email", "papel", "loja", "is_active")
    list_filter = ("papel", "loja", "is_active", "is_staff")

    fieldsets = UserAdmin.fieldsets + (
        ("Acesso ao sistema", {"fields": ("papel", "loja")}),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Acesso ao sistema", {"fields": ("first_name", "last_name", "email", "papel", "loja")}),
    )    