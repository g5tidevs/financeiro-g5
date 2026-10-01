from django import template

register = template.Library()


@register.filter
def atributo(obj, nome):
    """Uso no template: {{ objeto|atributo:"nome_do_campo" }}"""
    valor = getattr(obj, nome, "")
    return valor() if callable(valor) else valor