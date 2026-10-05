from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView

from .forms import DevolucaoPixForm
from .models import DevolucaoPix


class PixListView(ListView):
    template_name = "pix/lista.html"
    paginate_by = 50

    def get_queryset(self):
        return DevolucaoPix.objects.ativos().select_related("loja", "banco")


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