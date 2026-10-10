"""Cálculos do dashboard. Fica separado da view para ser fácil de ler e de testar."""

from datetime import date, timedelta

from django.db.models import Count, Q, Sum
from django.db.models.functions import TruncMonth
from django.urls import reverse
from django.utils import timezone

from apps.estornos.models import EstornoCartao
from apps.links.models import LinkPagamento
from apps.pix.models import DevolucaoPix

LINK_COMPLETO = Q(pago=True, no_caixa=True, nc_assinada=True, doc_enviado=True)
MESES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]


def _bases(loja=None):
    """Os três conjuntos de dados, já sem os excluídos e filtrados pela loja (se houver)."""
    pix = DevolucaoPix.objects.ativos()
    estornos = EstornoCartao.objects.ativos()
    links = LinkPagamento.objects.ativos()
    if loja:
        pix = pix.filter(loja=loja)
        estornos = estornos.filter(loja=loja)
        links = links.filter(vendedor__loja=loja)
    return pix, estornos, links


def resumo_periodo(inicio, fim, loja=None):
    pix, estornos, links = _bases(loja)
    periodo = {"data__gte": inicio, "data__lte": fim}

    r_pix = pix.filter(**periodo).aggregate(
        quantidade=Count("id"),
        total=Sum("valor"),
        pendente_ejl=Sum("valor", filter=Q(conciliado=False)),
    )
    r_estornos = estornos.filter(**periodo).aggregate(
        quantidade=Count("id"),
        total=Sum("valor"),
        sem_safra=Sum("valor", filter=Q(solicitado_banco=False)),
        pendente_ejl=Sum("valor", filter=Q(conciliado=False)),
    )
    r_links = links.filter(**periodo).aggregate(
        quantidade=Count("id"),
        total=Sum("valor"),
        completos=Count("id", filter=LINK_COMPLETO),
    )
    r_links["pendentes"] = r_links["quantidade"] - r_links["completos"]
    r_links["percentual"] = (
        round(100 * r_links["completos"] / r_links["quantidade"]) if r_links["quantidade"] else 0
    )
    return {"pix": r_pix, "estornos": r_estornos, "links": r_links}


def _meses_ate(fim, quantidade):
    """Primeiro dia de cada um dos últimos N meses, terminando no mês de 'fim'."""
    ano, mes = fim.year, fim.month
    meses = []
    for _ in range(quantidade):
        meses.append(date(ano, mes, 1))
        mes -= 1
        if mes == 0:
            ano, mes = ano - 1, 12
    return list(reversed(meses))


def evolucao_mensal(fim, loja=None, quantidade=12):
    pix, estornos, links = _bases(loja)
    meses = _meses_ate(fim, quantidade)
    desde = meses[0]

    def por_mes(qs, **agregacoes):
        linhas = (
            qs.filter(data__gte=desde, data__lte=fim)
            .annotate(mes=TruncMonth("data"))
            .values("mes")
            .annotate(**agregacoes)
        )
        return {linha["mes"]: linha for linha in linhas}

    m_pix = por_mes(pix, total=Sum("valor"))
    m_estornos = por_mes(estornos, total=Sum("valor"))
    m_links = por_mes(links, completos=Count("id", filter=LINK_COMPLETO), quantidade=Count("id"))

    def total(dados, mes):
        return float(dados.get(mes, {}).get("total") or 0)

    return {
        "rotulos": [f"{MESES[m.month - 1]}/{m:%y}" for m in meses],
        "pix": [total(m_pix, m) for m in meses],
        "estornos": [total(m_estornos, m) for m in meses],
        "links_completos": [m_links.get(m, {}).get("completos", 0) for m in meses],
        "links_pendentes": [
            m_links.get(m, {}).get("quantidade", 0) - m_links.get(m, {}).get("completos", 0) for m in meses
        ],
    }


def por_loja(inicio, fim):
    """Uma linha por loja com os totais do período, ordenada pelo maior volume de pendências."""
    pix, estornos, links = _bases()
    periodo = {"data__gte": inicio, "data__lte": fim}
    lojas = {}

    def linha(loja_id, nome):
        return lojas.setdefault(loja_id, {
            "nome": nome, "pix": 0, "estornos": 0, "links": 0,
            "pix_pendentes": 0, "estornos_pendentes": 0, "links_pendentes": 0,
        })

    for r in pix.filter(**periodo).values("loja", "loja__nome").annotate(
        total=Sum("valor"), pendentes=Count("id", filter=Q(conciliado=False))
    ):
        item = linha(r["loja"], r["loja__nome"])
        item["pix"], item["pix_pendentes"] = r["total"], r["pendentes"]

    for r in estornos.filter(**periodo).values("loja", "loja__nome").annotate(
        total=Sum("valor"),
        pendentes=Count("id", filter=Q(solicitado_banco=False) | Q(conciliado=False)),
    ):
        item = linha(r["loja"], r["loja__nome"])
        item["estornos"], item["estornos_pendentes"] = r["total"], r["pendentes"]

    for r in links.filter(**periodo).values("vendedor__loja", "vendedor__loja__nome").annotate(
        quantidade=Count("id"), pendentes=Count("id", filter=~LINK_COMPLETO)
    ):
        item = linha(r["vendedor__loja"], r["vendedor__loja__nome"])
        item["links"], item["links_pendentes"] = r["quantidade"], r["pendentes"]

    for item in lojas.values():
        item["total_pendencias"] = item["pix_pendentes"] + item["estornos_pendentes"] + item["links_pendentes"]
    return sorted(lojas.values(), key=lambda i: (-i["total_pendencias"], i["nome"]))


def pendencias_por_vendedor(inicio, fim, loja=None, limite=10):
    _, _, links = _bases(loja)
    linhas = (
        links.filter(data__gte=inicio, data__lte=fim)
        .exclude(LINK_COMPLETO)
        .values("vendedor__nome", "vendedor__loja__nome")
        .annotate(
            pendentes=Count("id"),
            falta_pago=Count("id", filter=Q(pago=False)),
            falta_caixa=Count("id", filter=Q(no_caixa=False)),
            falta_nc=Count("id", filter=Q(nc_assinada=False)),
            falta_doc=Count("id", filter=Q(doc_enviado=False)),
        )
        .order_by("-pendentes", "vendedor__nome")
    )
    return list(linhas[:limite])


def parados(dias, loja=None, limite=15):
    """Itens com pendência há mais de N dias, de qualquer período. Os mais antigos primeiro."""
    pix, estornos, links = _bases(loja)
    hoje = timezone.localdate()
    limite_data = hoje - timedelta(days=dias)

    pix = pix.filter(conciliado=False, data__lte=limite_data).select_related("loja")
    estornos = estornos.filter(
        Q(solicitado_banco=False) | Q(conciliado=False), data__lte=limite_data
    ).select_related("loja")
    links = links.pendentes().filter(data__lte=limite_data).select_related("vendedor__loja")

    # Conta tudo no banco, mas só traz os mais antigos de cada módulo
    contagem = {"Pix": pix.count(), "Estorno": estornos.count(), "Link": links.count()}

    itens = []
    for d in pix.order_by("data")[:limite]:
        itens.append({"modulo": "Pix", "data": d.data, "cliente": d.cliente, "loja": d.loja.nome,
                      "falta": "Conciliação EJL", "url": reverse("pix:editar", args=[d.pk])})
    for e in estornos.order_by("data")[:limite]:
        falta = [rotulo for rotulo, feito in [("Safra", e.solicitado_banco), ("EJL", e.conciliado)] if not feito]
        itens.append({"modulo": "Estorno", "data": e.data, "cliente": e.cliente, "loja": e.loja.nome,
                      "falta": ", ".join(falta), "url": reverse("estornos:editar", args=[e.pk])})
    for link in links.order_by("data")[:limite]:
        itens.append({"modulo": "Link", "data": link.data, "cliente": link.cliente,
                      "loja": link.vendedor.loja.nome, "falta": ", ".join(link.etapas_pendentes),
                      "url": reverse("links:editar", args=[link.pk])})

    itens.sort(key=lambda item: item["data"])
    for item in itens:
        item["dias"] = (hoje - item["data"]).days

    return {"contagem": contagem, "total": sum(contagem.values()), "itens": itens[:limite]}