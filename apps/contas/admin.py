from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import RegistroAcesso, Usuario
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

@admin.register(RegistroAcesso)
class RegistroAcessoAdmin(admin.ModelAdmin):
    list_display = ("data_hora", "tipo", "username", "detalhe", "ip")
    list_filter = ("tipo",)
    search_fields = ("username", "ip")
    date_hierarchy = "data_hora"

    # Log é só para consulta: ninguém cria, edita ou apaga pelo admin
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False    