from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils.functional import cached_property
from django.views import View
from django.views.generic import CreateView, FormView, ListView, UpdateView

from .forms import UsuarioCriarForm, UsuarioEditarForm, UsuarioSenhaForm
from .mixins import AdminRequiredMixin
from .models import Usuario


class UsuarioListView(AdminRequiredMixin, ListView):
    template_name = "contas/usuarios_lista.html"
    paginate_by = 50

    def get_queryset(self):
        qs = Usuario.objects.select_related("loja").order_by("first_name", "username")

        self.status = self.request.GET.get("status", "ativos")
        if self.status == "ativos":
            qs = qs.filter(is_active=True)
        elif self.status == "inativos":
            qs = qs.filter(is_active=False)

        self.q = self.request.GET.get("q", "").strip()
        if self.q:
            qs = qs.filter(
                Q(username__icontains=self.q)
                | Q(first_name__icontains=self.q)
                | Q(last_name__icontains=self.q)
                | Q(email__icontains=self.q)
            )
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["q"] = self.q
        context["status"] = self.status
        return context


class UsuarioCreateView(AdminRequiredMixin, CreateView):
    model = Usuario
    form_class = UsuarioCriarForm
    template_name = "contas/usuario_form.html"
    success_url = reverse_lazy("contas:usuarios")

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"Usuário criado: {self.object} ({self.object.username})")
        return response


class UsuarioUpdateView(AdminRequiredMixin, UpdateView):
    model = Usuario
    form_class = UsuarioEditarForm
    template_name = "contas/usuario_form.html"
    success_url = reverse_lazy("contas:usuarios")

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"Usuário salvo: {self.object}")
        return response


class UsuarioSenhaView(AdminRequiredMixin, FormView):
    """O administrador define uma nova senha para o usuário (sem precisar da antiga)."""

    form_class = UsuarioSenhaForm
    template_name = "contas/usuario_senha.html"

    @cached_property
    def usuario(self):
        return get_object_or_404(Usuario, pk=self.kwargs["pk"])

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.usuario
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["usuario"] = self.usuario
        return context

    def form_valid(self, form):
        form.save()
        # Se o administrador trocou a própria senha, mantém ele logado
        if self.usuario == self.request.user:
            update_session_auth_hash(self.request, self.usuario)
        messages.success(self.request, f"Senha alterada: {self.usuario}")
        return redirect("contas:usuarios")


class UsuarioAlternarView(AdminRequiredMixin, View):
    """Ativa ou desativa um usuário. Usuário desativado não consegue mais entrar."""

    http_method_names = ["post"]

    def post(self, request, pk):
        usuario = get_object_or_404(Usuario, pk=pk)
        status = request.POST.get("status", "ativos")
        destino = f"{reverse('contas:usuarios')}?status={status}"

        if usuario == request.user:
            messages.error(request, "Você não pode desativar o próprio usuário.")
            return redirect(destino)

        usuario.is_active = not usuario.is_active
        usuario.save(update_fields=["is_active"])

        if usuario.is_active:
            messages.success(request, f"Usuário reativado: {usuario}")
        else:
            messages.success(request, f"Usuário desativado: {usuario}. Ele não consegue mais entrar no sistema.")
        return redirect(destino)