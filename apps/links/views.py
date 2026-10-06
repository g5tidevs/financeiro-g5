from django.contrib import messages
from django.db.models import Count, Q, Sum
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, ListView, UpdateView

from apps.contas.mixins import SupervisorRequiredMixin
from apps.core.historico import montar_historico
from apps.core.utils import redirecionar_de_volta

from .forms import LinkFiltroForm, LinkPagamentoForm
from .models import LinkPagamento

ETAPAS = dict(LinkPagamento.ETAPAS)


class LinkListView(ListView):
    template_name = "links/lista.html"
    paginate_by = 50

    def get_queryset(self):
        self.filtro = LinkFiltroForm(self.request.GET or None)
        qs = LinkPagamento.objects.ativos().select_related("vendedor", "vendedor__loja")
        return self.filtro.filtrar(qs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filtro"] = self.filtro
        context["etapas"] = LinkPagamento.ETAPAS

        resumo = self.object_list.aggregate(
            quantidade=Count("id"),
            total=Sum("valor"),
            completos=Count("id", filter=Q(pago=True, no_caixa=True, nc_assinada=True, doc_enviado=True)),
            **{f"falta_{campo}": Count("id", filter=Q(**{campo: False})) for campo in ETAPAS},
        )
        resumo["pendentes"] = resumo["quantidade"] - resumo["completos"]
        context["resumo"] = resumo

        # Atalhos "Falta X": mantêm os outros filtros e trocam só a situação
        params = self.request.GET.copy()
        params.pop("page", None)
        atalhos = []
        for campo, rotulo in LinkPagamento.ETAPAS:
            p = params.copy()
            p["situacao"] = campo
            atalhos.append({
                "rotulo": rotulo,
                "quantidade": resumo[f"falta_{campo}"],
                "url": "?" + p.urlencode(),
                "ativo": params.get("situacao") == campo,
            })
        context["atalhos"] = atalhos

        context["filtros_url"] = params.urlencode()
        context["tem_filtro"] = any(valor for valor in params.values())
        return context


class LinkFormMixin:
    model = LinkPagamento
    form_class = LinkPagamentoForm
    template_name = "links/form.html"
    success_url = reverse_lazy("links:lista")

    def form_valid(self, form):
        if not form.instance.pk:
            form.instance.criado_por = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, f"Link salvo: {self.object.cliente}")

        if "salvar_e_novo" in self.request.POST:
            return redirect("links:novo")
        return response


class LinkCreateView(LinkFormMixin, CreateView):
    pass


class LinkUpdateView(LinkFormMixin, UpdateView):
    def get_queryset(self):
        return LinkPagamento.objects.ativos()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["historico"] = montar_historico(self.object)
        return context


class LinkEtapaView(View):
    """Marca ou desmarca uma etapa do checklist direto da lista."""

    http_method_names = ["post"]

    def post(self, request, pk, campo):
        if campo not in ETAPAS:
            raise Http404("Etapa inválida")
        link = get_object_or_404(LinkPagamento.objects.ativos(), pk=pk)
        novo_valor = not getattr(link, campo)

        # Mesma regra do formulário: link pago precisa de NSU
        if campo == "pago" and novo_valor and not link.nsu:
            messages.warning(request, f"Informe o NSU de {link.cliente} para marcar o link como pago.")
            return redirect("links:editar", pk=link.pk)

        setattr(link, campo, novo_valor)
        link.save(update_fields=[campo, "atualizado_em"])

        situacao = "marcado" if novo_valor else "desmarcado"
        messages.success(request, f"{ETAPAS[campo]} {situacao}: {link.cliente}")
        return redirecionar_de_volta(request, "links:lista")


class LinkExcluirView(SupervisorRequiredMixin, View):
    """Exclusão lógica: some das listas e totais, mas continua no banco e no histórico."""

    http_method_names = ["post"]

    def post(self, request, pk):
        link = get_object_or_404(LinkPagamento.objects.ativos(), pk=pk)
        link.ativo = False
        link.save(update_fields=["ativo", "atualizado_em"])
        messages.success(request, f"Link excluído: {link}")
        return redirect("links:lista")