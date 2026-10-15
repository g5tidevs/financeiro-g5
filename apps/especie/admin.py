from django.contrib import admin

from apps.core.admin import ModeloBaseAdmin

from .models import DevolucaoEspecie


@admin.register(DevolucaoEspecie)
class DevolucaoEspecieAdmin(ModeloBaseAdmin):
    list_display = ("data", "loja", "cliente", "valor", "motivo", "ativo")
    list_filter = ("ativo", "loja")
    search_fields = ("cliente", "motivo")
    date_hierarchy = "data"
    list_select_related = ("loja",)