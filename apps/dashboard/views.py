from datetime import timedelta
from urllib.parse import urlencode

from django.urls import reverse
from django.utils import timezone
from django.views.generic import TemplateView

from apps.contas.mixins import SupervisorRequiredMixin

from . import services
from .forms import DashboardFiltroForm


class DashboardView(SupervisorRequiredMixin, TemplateView):
    template_name = "dashboard/painel.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        hoje = timezone.localdate()

        # Padrão: mês atual, todas as lojas, parados há mais de 7 dias.
        # O que vier preenchido na URL substitui o padrão.
        padrao = {"inicio": hoje.replace(day=1).isoformat(), "fim": hoje.isoformat(), "dias": "7"}
        dados = {**padrao, **{chave: valor for chave, valor in self.request.GET.items() if valor}}
        filtro = DashboardFiltroForm(dados)

        if filtro.is_valid():
            inicio = filtro.cleaned_data["inicio"]
            fim = filtro.cleaned_data["fim"]
            loja = filtro.cleaned_data["loja"]
            dias = filtro.cleaned_data["dias"]
        else:
            inicio, fim, loja, dias = hoje.replace(day=1), hoje, None, 7

        context.update({
            "filtro": filtro,
            "inicio": inicio,
            "fim": fim,
            "loja": loja,
            "dias": dias,
            "resumo": services.resumo_periodo(inicio, fim, loja),
            "grafico": services.evolucao_mensal(fim, loja),
            "por_loja": None if loja else services.por_loja(inicio, fim),
            "vendedores": services.pendencias_por_vendedor(inicio, fim, loja),
            "parados": services.parados(dias, loja),
            "periodos": self._atalhos_periodo(hoje, loja, dias),
            "listas": self._links_para_listas(inicio, fim, loja),
        })
        return context

    def _atalhos_periodo(self, hoje, loja, dias):
        inicio_mes = hoje.replace(day=1)
        fim_mes_passado = inicio_mes - timedelta(days=1)
        opcoes = [
            ("Este mês", inicio_mes, hoje),
            ("Mês passado", fim_mes_passado.replace(day=1), fim_mes_passado),
            ("Últimos 90 dias", hoje - timedelta(days=89), hoje),
            ("Este ano", hoje.replace(month=1, day=1), hoje),
        ]
        atalhos = []
        for rotulo, inicio, fim in opcoes:
            params = {"inicio": inicio.isoformat(), "fim": fim.isoformat(), "dias": dias}
            if loja:
                params["loja"] = loja.pk
            atalhos.append({"rotulo": rotulo, "url": "?" + urlencode(params)})
        return atalhos

    def _links_para_listas(self, inicio, fim, loja):
        """Endereços das listas de cada módulo, já filtradas com o mesmo período e loja."""
        base = {"inicio": inicio.isoformat(), "fim": fim.isoformat()}
        if loja:
            base["loja"] = loja.pk
        return {
            "pix": reverse("pix:lista") + "?" + urlencode({**base, "situacao": "pendente"}),
            "estornos": reverse("estornos:lista") + "?" + urlencode(base),
            "links": reverse("links:lista") + "?" + urlencode({**base, "situacao": "pendente"}),
        }