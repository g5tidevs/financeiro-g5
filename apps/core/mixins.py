from django.db import IntegrityError, transaction


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