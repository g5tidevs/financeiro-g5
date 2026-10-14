from decimal import Decimal

from django import template
from django.utils.html import format_html

register = template.Library()


@register.filter
def atributo(obj, nome):
    """Uso no template: {{ objeto|atributo:"nome_do_campo" }}"""
    valor = getattr(obj, nome, "")
    return valor() if callable(valor) else valor


@register.filter
def brl(valor):
    """Formata como dinheiro: 1234.5 -> R$ 1.234,50"""
    if valor in (None, ""):
        return "—"
    valor = Decimal(valor).quantize(Decimal("0.01"))
    inteiro, centavos = f"{valor:,.2f}".split(".")
    return f"R$ {inteiro.replace(',', '.')},{centavos}"


@register.filter
def dinheiro(valor):
    """Igual ao brl, mas com o "R$" num span para o CSS deixá-lo mais discreto que o número."""
    texto = brl(valor)
    if not texto.startswith("R$ "):
        return texto
    return format_html('<span class="moeda">R$</span>&nbsp;{}', texto[3:])