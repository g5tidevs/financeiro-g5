from django.contrib import admin

from apps.core.admin import ModeloBaseAdmin

from .models import DevolucaoPix


@admin.register(DevolucaoPix)
class DevolucaoPixAdmin(ModeloBaseAdmin):
    list_display = ("data", "loja", "cliente", "valor", "banco", "motivo", "conciliado", "ativo")
    list_filter = ("conciliado", "ativo", "loja", "banco")
    search_fields = ("cliente", "motivo")
    date_hierarchy = "data"
    list_select_related = ("loja", "banco")