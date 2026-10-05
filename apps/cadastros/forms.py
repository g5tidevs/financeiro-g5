from django.db.models import Q

from apps.core.forms import BootstrapModelForm

from .models import Banco, Loja, Vendedor


class LojaForm(BootstrapModelForm):
    class Meta:
        model = Loja
        fields = ["nome", "codigo"]


class VendedorForm(BootstrapModelForm):
    class Meta:
        model = Vendedor
        fields = ["nome", "loja"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Só lojas ativas, mas mantém a loja atual do vendedor caso ela tenha sido desativada
        self.fields["loja"].queryset = Loja.objects.filter(
            Q(ativo=True) | Q(pk=self.instance.loja_id)
        )


class BancoForm(BootstrapModelForm):
    class Meta:
        model = Banco
        fields = ["codigo", "nome"]

