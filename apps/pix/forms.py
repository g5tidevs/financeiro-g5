from django import forms
from django.db.models import Count, Q
from django.utils import timezone

from apps.cadastros.models import Banco, Loja
from apps.core.forms import BootstrapFormMixin, BootstrapModelForm, ValorBRField

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


class PixFiltroForm(BootstrapFormMixin, forms.Form):
    SITUACOES = [
        ("", "Todas"),
        ("pendente", "Pendentes"),
        ("conciliado", "Conciliadas"),
    ]

    inicio = forms.DateField(
        label="De", required=False,
        widget=forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
    )
    fim = forms.DateField(
        label="Até", required=False,
        widget=forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
    )
    loja = forms.ModelChoiceField(label="Loja", queryset=Loja.objects.all(), required=False, empty_label="Todas")
    banco = forms.ModelChoiceField(label="Banco", queryset=Banco.objects.all(), required=False, empty_label="Todos")
    situacao = forms.ChoiceField(label="EJL", choices=SITUACOES, required=False)
    q = forms.CharField(
        label="Buscar", required=False,
        widget=forms.TextInput(attrs={"type": "search", "placeholder": "Cliente ou motivo"}),
    )

    def clean(self):
        dados = super().clean()
        inicio, fim = dados.get("inicio"), dados.get("fim")
        if inicio and fim and inicio > fim:
            raise forms.ValidationError("A data inicial não pode ser depois da data final.")
        return dados

    def filtrar(self, qs):
        """Aplica os filtros preenchidos. Se o formulário tiver erro, não filtra nada."""
        if not self.is_valid():
            return qs
        d = self.cleaned_data
        if d["inicio"]:
            qs = qs.filter(data__gte=d["inicio"])
        if d["fim"]:
            qs = qs.filter(data__lte=d["fim"])
        if d["loja"]:
            qs = qs.filter(loja=d["loja"])
        if d["banco"]:
            qs = qs.filter(banco=d["banco"])
        if d["situacao"] == "pendente":
            qs = qs.filter(conciliado=False)
        elif d["situacao"] == "conciliado":
            qs = qs.filter(conciliado=True)
        if d["q"]:
            qs = qs.filter(Q(cliente__icontains=d["q"]) | Q(motivo__icontains=d["q"]))
        return qs