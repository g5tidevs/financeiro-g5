from django.db import IntegrityError, transaction
from django.urls import reverse
from django.utils.cache import patch_vary_headers

from .historico import montar_historico


class NsuUnicoMixin:
    """Se duas pessoas salvarem o mesmo NSU ao mesmo tempo, o banco recusa a segunda.

    Em vez de uma página de erro, a pessoa volta ao formulário com uma mensagem clara.
    """

    def form_valid(self, form):
        try:
            with transaction.atomic():
                return super().form_valid(form)
        except IntegrityError:
            form.add_error(
                "nsu",
                "Este NSU acabou de ser lançado por outra pessoa. Confira a lista antes de salvar de novo.",
            )
            return self.form_invalid(form)


class DetalheMixin:
    """Detalhes de um lançamento, com o histórico de alterações.

    A lista busca esta página via fetch e mostra só o conteúdo, num painel lateral.
    Aberta direto (Ctrl+clique, nova aba), vira uma página comum com o mesmo conteúdo.
    """

    def no_painel(self):
        return self.request.headers.get("X-Requested-With") == "XMLHttpRequest"

    def get_template_names(self):
        return [self.template_name] if self.no_painel() else ["core/detalhe_pagina.html"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        modulo = self.request.resolver_match.app_name
        context.update({
            "fragmento": self.template_name,
            "pagina": not self.no_painel(),
            "modulo": self.object._meta.verbose_name,
            "lista_url": reverse(f"{modulo}:lista"),
            "editar_url": reverse(f"{modulo}:editar", args=[self.object.pk]),
            "historico": montar_historico(self.object),
        })
        return context

    def render_to_response(self, context, **response_kwargs):
        response = super().render_to_response(context, **response_kwargs)
        # A mesma URL devolve o painel ou a página inteira: o navegador não pode trocar um pelo outro no cache
        patch_vary_headers(response, ["X-Requested-With"])
        return response
