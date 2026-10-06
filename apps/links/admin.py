from django.contrib import admin

from apps.core.admin import ModeloBaseAdmin

from .models import LinkPagamento


@admin.register(LinkPagamento)
class LinkPagamentoAdmin(ModeloBaseAdmin):
    list_display = ("data", "vendedor", "cliente", "parcelas", "valor", "nsu",
                    "pago", "no_caixa", "nc_assinada", "doc_enviado", "ativo")
    list_filter = ("pago", "no_caixa", "nc_assinada", "doc_enviado", "ativo", "vendedor__loja")
    search_fields = ("cliente", "nsu", "vendedor__nome")
    date_hierarchy = "data"
    list_select_related = ("vendedor", "vendedor__loja")