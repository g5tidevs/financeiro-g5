from django.contrib import admin

from apps.core.admin import ModeloBaseAdmin

from .models import Banco, Loja, Vendedor


@admin.register(Loja)
class LojaAdmin(ModeloBaseAdmin):
    list_display = ("nome", "codigo", "ativo")
    list_filter = ("ativo",)
    search_fields = ("nome", "codigo")


@admin.register(Vendedor)
class VendedorAdmin(ModeloBaseAdmin):
    list_display = ("nome", "loja", "ativo")
    list_filter = ("ativo", "loja")
    search_fields = ("nome",)
    list_select_related = ("loja",)


@admin.register(Banco)
class BancoAdmin(ModeloBaseAdmin):
    list_display = ("nome", "codigo", "ativo")
    list_filter = ("ativo",)
    search_fields = ("nome", "codigo")

