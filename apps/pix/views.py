from django.contrib import messages
from django.db.models import Count, Q, Sum
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, ListView, UpdateView

from apps.contas.mixins import SupervisorRequiredMixin
from apps.core.utils import redirecionar_de_volta

from .forms import DevolucaoPixForm, PixFiltroForm
from .models import DevolucaoPix


class PixListView(ListView):
    template_name = "pix/lista.html"
    paginate_by = 50

    def get_queryset(self):
        self.filtro = PixFiltroForm(self.request.GET or None)
        qs = DevolucaoPix.objects.ativos().select_related("loja", "banco")
        return self.filtro.filtrar(qs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filtro"] = self.filtro

        # Totais de TUDO que passou no filtro (não só da página atual)
        context["resumo"] = self.object_list.aggregate(
            quantidade=Count("id"),
            total=Sum("valor"),
            pendentes=Count("id", filter=Q(conciliado=False)),
            total_pendente=Sum("valor", filter=Q(conciliado=False)),
        )

        # Filtros atuais, para a paginação não perdê-los
        params = self.request.GET.copy()
        params.pop("page", None)
        context["filtros_url"] = params.urlencode()
        context["tem_filtro"] = any(valor for valor in params.values())
        return context


class PixFormMixin:
    model = DevolucaoPix
    form_class = DevolucaoPixForm
    template_name = "pix/form.html"
    success_url = reverse_lazy("pix:lista")

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
            return redirect("pix:novo")
        return response


class PixCreateView(PixFormMixin, CreateView):
    pass


class PixUpdateView(PixFormMixin, UpdateView):
    def get_queryset(self):
        return DevolucaoPix.objects.ativos()


class PixConciliarView(View):
    """Marca ou desmarca a conciliação direto da lista."""

    http_method_names = ["post"]

    def post(self, request, pk):
        devolucao = get_object_or_404(DevolucaoPix.objects.ativos(), pk=pk)
        devolucao.conciliado = not devolucao.conciliado
        devolucao.save(update_fields=["conciliado", "atualizado_em"])

        if devolucao.conciliado:
            messages.success(request, f"Marcada como conciliada: {devolucao.cliente}")
        else:
            messages.info(request, f"Voltou para pendente: {devolucao.cliente}")
        return redirecionar_de_volta(request, "pix:lista")


class PixExcluirView(SupervisorRequiredMixin, View):
    """Exclusão lógica: some das listas e totais, mas continua no banco e no histórico."""

    http_method_names = ["post"]

    def post(self, request, pk):
        devolucao = get_object_or_404(DevolucaoPix.objects.ativos(), pk=pk)
        devolucao.ativo = False
        devolucao.save(update_fields=["ativo", "atualizado_em"])
        messages.success(request, f"Devolução excluída: {devolucao}")
        return redirect("pix:lista")