from django.contrib import messages
from django.db.models import Count, Q, Sum
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, ListView, UpdateView

from apps.contas.mixins import SupervisorRequiredMixin
from apps.core.historico import montar_historico
from apps.core.utils import redirecionar_de_volta

from .forms import EstornoCartaoForm, EstornoFiltroForm
from .models import EstornoCartao


class EstornoListView(ListView):
    template_name = "estornos/lista.html"
    paginate_by = 50

    def get_queryset(self):
        self.filtro = EstornoFiltroForm(self.request.GET or None)
        qs = EstornoCartao.objects.ativos().select_related("loja")
        return self.filtro.filtrar(qs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filtro"] = self.filtro
        context["resumo"] = self.object_list.aggregate(
            quantidade=Count("id"),
            total=Sum("valor"),
            sem_safra=Count("id", filter=Q(solicitado_banco=False)),
            total_sem_safra=Sum("valor", filter=Q(solicitado_banco=False)),
            sem_ejl=Count("id", filter=Q(conciliado=False)),
            total_sem_ejl=Sum("valor", filter=Q(conciliado=False)),
        )
        params = self.request.GET.copy()
        params.pop("page", None)
        context["filtros_url"] = params.urlencode()
        context["tem_filtro"] = any(valor for valor in params.values())
        return context


class EstornoFormMixin:
    model = EstornoCartao
    form_class = EstornoCartaoForm
    template_name = "estornos/form.html"
    success_url = reverse_lazy("estornos:lista")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["usuario"] = self.request.user
        return kwargs

    def form_valid(self, form):
        if not form.instance.pk:
            form.instance.criado_por = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, f"Estorno salvo: {self.object}")

        if "salvar_e_novo" in self.request.POST:
            return redirect("estornos:novo")
        return response


class EstornoCreateView(EstornoFormMixin, CreateView):
    pass


class EstornoUpdateView(EstornoFormMixin, UpdateView):
    def get_queryset(self):
        return EstornoCartao.objects.ativos()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["historico"] = montar_historico(self.object)
        return context


class EstornoAlternarView(View):
    """Marca ou desmarca uma etapa (Safra ou EJL) direto da lista.

    O campo é definido na URL: as_view(campo="conciliado") ou as_view(campo="solicitado_banco").
    """

    http_method_names = ["post"]
    campo = None

    MENSAGENS = {
        "solicitado_banco": ("Marcado como solicitado no Safra", "Voltou para não solicitado no Safra"),
        "conciliado": ("Marcado como conciliado na EJL", "Voltou para pendente na EJL"),
    }

    def post(self, request, pk):
        estorno = get_object_or_404(EstornoCartao.objects.ativos(), pk=pk)
        novo_valor = not getattr(estorno, self.campo)
        setattr(estorno, self.campo, novo_valor)
        estorno.save(update_fields=[self.campo, "atualizado_em"])

        marcado, desmarcado = self.MENSAGENS[self.campo]
        if novo_valor:
            messages.success(request, f"{marcado}: {estorno.cliente}")
        else:
            messages.info(request, f"{desmarcado}: {estorno.cliente}")
        return redirecionar_de_volta(request, "estornos:lista")


class EstornoExcluirView(SupervisorRequiredMixin, View):
    """Exclusão lógica: some das listas e totais, mas continua no banco e no histórico."""

    http_method_names = ["post"]

    def post(self, request, pk):
        estorno = get_object_or_404(EstornoCartao.objects.ativos(), pk=pk)
        estorno.ativo = False
        estorno.save(update_fields=["ativo", "atualizado_em"])
        messages.success(request, f"Estorno excluído: {estorno}")
        return redirect("estornos:lista")