from django.contrib import admin

from apps.core.admin import ModeloBaseAdmin

from .models import EstornoCartao


@admin.register(EstornoCartao)
class EstornoCartaoAdmin(ModeloBaseAdmin):
    list_display = ("data", "loja", "cliente", "valor", "nsu", "solicitado_banco", "conciliado", "ativo")
    list_filter = ("solicitado_banco", "conciliado", "ativo", "loja")
    search_fields = ("cliente", "nsu", "motivo", "contato_cliente")
    date_hierarchy = "data"
    list_select_related = ("loja",)