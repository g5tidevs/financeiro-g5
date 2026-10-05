from django import forms
from django.db.models import Count, Q
from django.utils import timezone

from apps.cadastros.models import Banco, Loja
from apps.core.forms import BootstrapModelForm, ValorBRField

from .models import DevolucaoPix


class DevolucaoPixForm(BootstrapModelForm):
    valor = ValorBRField(label="Valor")

    class Meta:
        model = DevolucaoPix
        fields = ["data", "loja", "cliente", "valor", "banco", "motivo", "conciliado"]
        widgets = {
            "data": forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
            "motivo": forms.TextInput(attrs={"list": "motivos-sugeridos", "autocomplete": "off"}),
        }

    def __init__(self, *args, usuario=None, **kwargs):
        super().__init__(*args, **kwargs)
        inst = self.instance

        # Listas só com cadastros ativos (mantendo o valor atual ao editar)
        self.fields["loja"].queryset = Loja.objects.filter(Q(ativo=True) | Q(pk=inst.loja_id))
        self.fields["banco"].queryset = Banco.objects.filter(Q(ativo=True) | Q(pk=inst.banco_id))

        # Em um lançamento novo: data de hoje e a loja do usuário já preenchidas
        if not inst.pk:
            self.fields["data"].initial = timezone.localdate()
            if usuario and usuario.loja_id:
                self.fields["loja"].initial = usuario.loja_id

    def sugestoes_motivo(self):
        """Os 30 motivos mais usados, para sugerir enquanto o usuário digita."""
        return (
            DevolucaoPix.objects.ativos()
            .values_list("motivo", flat=True)
            .annotate(usos=Count("id"))
            .order_by("-usos", "motivo")[:30]
        )

    def clean_motivo(self):
        # Remove espaços sobrando e começa com letra maiúscula
        motivo = " ".join(self.cleaned_data["motivo"].split())
        return motivo[:1].upper() + motivo[1:]