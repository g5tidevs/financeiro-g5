from django.contrib import messages
from django.db.models import Count, Sum
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from apps.contas.mixins import SupervisorRequiredMixin
from apps.core.historico import montar_historico
from apps.core.mixins import DetalheMixin

from .forms import DevolucaoEspecieForm, EspecieFiltroForm
from .models import DevolucaoEspecie


class EspecieListView(ListView):
    template_name = "especie/lista.html"
    paginate_by = 50

    def get_queryset(self):
        self.filtro = EspecieFiltroForm(self.request.GET or None)
        qs = DevolucaoEspecie.objects.ativos().select_related("loja")
        return self.filtro.filtrar(qs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filtro"] = self.filtro
        context["resumo"] = self.object_list.aggregate(quantidade=Count("id"), total=Sum("valor"))

        params = self.request.GET.copy()
        params.pop("page", None)
        context["filtros_url"] = params.urlencode()
        context["tem_filtro"] = any(valor for valor in params.values())
        return context


class EspecieDetalheView(DetalheMixin, DetailView):
    template_name = "especie/detalhe.html"
    queryset = DevolucaoEspecie.objects.ativos().select_related("loja", "criado_por")


class EspecieFormMixin:
    model = DevolucaoEspecie
    form_class = DevolucaoEspecieForm
    template_name = "especie/form.html"
    success_url = reverse_lazy("especie:lista")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["usuario"] = self.request.user
        return kwargs

    def form_valid(self, form):
        if not form.instance.pk:
            form.instance.criado_por = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, f"Devolução salva: {self.object.cliente}")

        if "salvar_e_novo" in self.request.POST:
            return redirect("especie:novo")
        return response


class EspecieCreateView(EspecieFormMixin, CreateView):
    pass


class EspecieUpdateView(EspecieFormMixin, UpdateView):
    def get_queryset(self):
        return DevolucaoEspecie.objects.ativos()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["historico"] = montar_historico(self.object)
        return context


class EspecieExcluirView(SupervisorRequiredMixin, View):
    """Exclusão lógica: some das listas e totais, mas continua no banco e no histórico."""

    http_method_names = ["post"]

    def post(self, request, pk):
        devolucao = get_object_or_404(DevolucaoEspecie.objects.ativos(), pk=pk)
        devolucao.ativo = False
        devolucao.save(update_fields=["ativo", "atualizado_em"])
        messages.success(request, f"Devolução excluída: {devolucao}")
        return redirect("especie:lista")


