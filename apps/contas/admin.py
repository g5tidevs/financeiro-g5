from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ("username", "get_full_name", "email", "papel", "is_active")
    list_filter = ("papel", "is_active", "is_staff")

    # Tela de edição: adiciona o campo papel aos campos padrão
    fieldsets = UserAdmin.fieldsets + (
        ("Acesso ao sistema", {"fields": ("papel",)}),
    )

    # Tela de criação: já permite definir nome, e-mail e papel
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Acesso ao sistema", {"fields": ("first_name", "last_name", "email", "papel")}),
    )