from datetime import date
from decimal import Decimal

from django.db import models

from apps.core.templatetags.core_tags import brl

ACOES = {"+": "Criado", "~": "Alterado", "-": "Removido"}

# Campos que mudam sozinhos e não interessam a quem lê o histórico
IGNORADOS = ["criado_em", "atualizado_em", "criado_por"]


def _formatar(campo, valor):
    """Deixa o valor legível: Sim/Não, R$, datas no formato brasileiro."""
    if valor in (None, ""):
        return "—"
    if isinstance(campo, models.BooleanField):
        return "Sim" if valor else "Não"
    if isinstance(valor, Decimal):
        return brl(valor)
    if isinstance(valor, date):
        return valor.strftime("%d/%m/%Y")
    return str(valor)


def montar_historico(obj, limite=50):
    """Lista as alterações de um registro, da mais recente para a mais antiga."""
    registros = list(
        obj.history.select_related("history_user").order_by("-history_date", "-history_id")[: limite + 1]
    )

    itens = []
    for i, registro in enumerate(registros[:limite]):
        anterior = registros[i + 1] if i + 1 < len(registros) else None

        mudancas = []
        if registro.history_type == "~" and anterior:
            delta = registro.diff_against(anterior, excluded_fields=IGNORADOS, foreign_keys_are_objs=True)
            for mudanca in delta.changes:
                campo = obj._meta.get_field(mudanca.field)
                mudancas.append({
                    "campo": campo.verbose_name,
                    "de": _formatar(campo, mudanca.old),
                    "para": _formatar(campo, mudanca.new),
                })
            if not mudancas:
                continue  # salvou sem mudar nada: não poluir o histórico

        itens.append({
            "acao": ACOES.get(registro.history_type, registro.history_type),
            "usuario": registro.history_user,
            "data": registro.history_date,
            "mudancas": mudancas,
        })
    return itens