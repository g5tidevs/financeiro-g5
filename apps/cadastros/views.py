from django.contrib import messages
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import CreateView, ListView, UpdateView

from apps.contas.mixins import SupervisorRequiredMixin

from .forms import BancoForm, LojaForm, VendedorForm
from .models import Banco, Loja, Vendedor

# Cada cadastro do sistema é uma entrada neste dicionário.
# A chave é o trecho da URL: /cadastros/lojas/, /cadastros/vendedores/ ...
CADASTROS = {
    "lojas": {
        "model": Loja,
        "form": LojaForm,
        "titulo": "Lojas",
        "novo": "Nova loja",
        "colunas": [("Nome", "nome"), ("Código", "codigo")],
        "busca": ["nome", "codigo"],
    },
    "vendedores": {
        "model": Vendedor,
        "form": VendedorForm,
        "titulo": "Vendedores",
        "novo": "Novo vendedor",
        "colunas": [("Nome", "nome"), ("Loja", "loja")],
        "busca": ["nome", "loja__nome"],
        "select_related": ["loja"],
    },
    "bancos": {
        "model": Banco,
        "form": BancoForm,
        "titulo": "Bancos",
        "novo": "Novo banco",
        "colunas": [("Código", "codigo"), ("Nome", "nome")],
        "busca": ["nome", "codigo"],
    },
}


class CadastroMixin(SupervisorRequiredMixin):
    """Descobre pela URL qual cadastro está sendo usado."""

    def dispatch(self, request, *args, **kwargs):
        self.entidade = kwargs["entidade"]
        self.config = CADASTROS.get(self.entidade)
        if self.config is None:
            raise Http404("Cadastro não encontrado")
        self.model = self.config["model"]
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["entidade"] = self.entidade
        context["config"] = self.config
        context["abas"] = [(slug, c["titulo"]) for slug, c in CADASTROS.items()]
        return context


class CadastroListView(CadastroMixin, ListView):
    template_name = "cadastros/lista.html"
    paginate_by = 25

    def get_queryset(self):
        qs = self.model.objects.all()
        if self.config.get("select_related"):
            qs = qs.select_related(*self.config["select_related"])

        self.status = self.request.GET.get("status", "ativos")
        if self.status == "ativos":
            qs = qs.filter(ativo=True)
        elif self.status == "inativos":
            qs = qs.filter(ativo=False)

        self.q = self.request.GET.get("q", "").strip()
        if self.q:
            filtro = Q()
            for campo in self.config["busca"]:
                filtro |= Q(**{f"{campo}__icontains": self.q})
            qs = qs.filter(filtro)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["q"] = self.q
        context["status"] = self.status
        return context


class CadastroFormMixin(CadastroMixin):
    template_name = "cadastros/form.html"

    def get_form_class(self):
        return self.config["form"]

    def get_success_url(self):
        return reverse("cadastros:lista", args=[self.entidade])

    def form_valid(self, form):
        if not form.instance.pk:
            form.instance.criado_por = self.request.user
        messages.success(self.request, f"Cadastro salvo: {form.instance}")
        return super().form_valid(form)


class CadastroCreateView(CadastroFormMixin, CreateView):
    pass


class CadastroUpdateView(CadastroFormMixin, UpdateView):
    pass


class CadastroAlternarView(CadastroMixin, View):
    """Ativa ou desativa um cadastro. Só aceita POST."""

    http_method_names = ["post"]

    def post(self, request, entidade, pk):
        obj = get_object_or_404(self.model, pk=pk)
        obj.ativo = not obj.ativo
        obj.save(update_fields=["ativo", "atualizado_em"])

        acao = "reativado" if obj.ativo else "desativado"
        messages.success(request, f"Cadastro {acao}: {obj}")

        status = request.POST.get("status", "ativos")
        return redirect(f"{reverse('cadastros:lista', args=[entidade])}?status={status}")