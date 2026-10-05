from django import forms
from django.db.models import Q
from django.utils import timezone

from apps.cadastros.models import Banco, Loja, Motivo
from apps.core.forms import BootstrapModelForm, ValorBRField

from .models import DevolucaoPix


class DevolucaoPixForm(BootstrapModelForm):
    valor = ValorBRField(label="Valor")

    class Meta:
        model = DevolucaoPix
        fields = ["data", "loja", "cliente", "valor", "banco", "motivo", "conciliado"]
        widgets = {
            "data": forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
        }

    def __init__(self, *args, usuario=None, **kwargs):
        super().__init__(*args, **kwargs)
        inst = self.instance

        # Listas só com cadastros ativos (mantendo o valor atual ao editar)
        self.fields["loja"].queryset = Loja.objects.filter(Q(ativo=True) | Q(pk=inst.loja_id))
        self.fields["banco"].queryset = Banco.objects.filter(Q(ativo=True) | Q(pk=inst.banco_id))
        self.fields["motivo"].queryset = Motivo.objects.filter(tipo=Motivo.Tipo.PIX).filter(
            Q(ativo=True) | Q(pk=inst.motivo_id)
        )

        # Em um lançamento novo: data de hoje e a loja do usuário já preenchidas
        if not inst.pk:
            self.fields["data"].initial = timezone.localdate()
            if usuario and usuario.loja_id:
                self.fields["loja"].initial = usuario.loja_id