from django import forms
from django.db.models import Q
from django.utils import timezone

from apps.cadastros.models import Loja, Vendedor
from apps.core.forms import BootstrapFormMixin, BootstrapModelForm, ValorBRField

from .models import LinkPagamento

CAMPO_DATA = forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"})


class LinkPagamentoForm(BootstrapModelForm):
    valor = ValorBRField(label="Valor", required=False)

    class Meta:
        model = LinkPagamento
        fields = ["data", "vendedor", "cliente", "parcelas", "valor", "nsu",
                  "pago", "no_caixa", "nc_assinada", "doc_enviado"]
        widgets = {
            "data": CAMPO_DATA,
            "parcelas": forms.NumberInput(attrs={"min": 1, "max": 24}),
            "nsu": forms.TextInput(attrs={"inputmode": "numeric", "autocomplete": "off"}),
        }
        help_texts = {
            "nsu": "Obrigatório quando o link estiver pago.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        inst = self.instance

        self.fields["vendedor"].queryset = (
            Vendedor.objects.filter(Q(ativo=True) | Q(pk=inst.vendedor_id))
            .select_related("loja")
            .order_by("loja__nome", "nome")
        )

        if not inst.pk:
            self.fields["data"].initial = timezone.localdate()

    def clean_nsu(self):
        nsu = self.cleaned_data["nsu"]
        return "".join(c for c in nsu if c.isdigit()) or nsu.strip()

    def campos_etapas(self):
        """Os quatro checkboxes do checklist, na ordem, para o template."""
        return [self[campo] for campo, _ in LinkPagamento.ETAPAS]


class LinkFiltroForm(BootstrapFormMixin, forms.Form):
    SITUACOES = [("", "Todos"), ("pendente", "Com pendência"), ("completo", "Completos")] + [
        (campo, f"Falta: {rotulo}") for campo, rotulo in LinkPagamento.ETAPAS
    ]

    inicio = forms.DateField(label="De", required=False, widget=CAMPO_DATA)
    fim = forms.DateField(label="Até", required=False, widget=CAMPO_DATA)
    loja = forms.ModelChoiceField(label="Loja", queryset=Loja.objects.all(), required=False, empty_label="Todas")
    vendedor = forms.ModelChoiceField(
        label="Vendedor",
        queryset=Vendedor.objects.select_related("loja").order_by("nome"),
        required=False,
        empty_label="Todos",
    )
    situacao = forms.ChoiceField(label="Situação", choices=SITUACOES, required=False)
    q = forms.CharField(
        label="Buscar", required=False,
        widget=forms.TextInput(attrs={"type": "search", "placeholder": "Cliente ou NSU"}),
    )

    def clean(self):
        dados = super().clean()
        inicio, fim = dados.get("inicio"), dados.get("fim")
        if inicio and fim and inicio > fim:
            raise forms.ValidationError("A data inicial não pode ser depois da data final.")
        return dados

    def filtrar(self, qs):
        if not self.is_valid():
            return qs
        d = self.cleaned_data
        if d["inicio"]:
            qs = qs.filter(data__gte=d["inicio"])
        if d["fim"]:
            qs = qs.filter(data__lte=d["fim"])
        if d["loja"]:
            qs = qs.filter(vendedor__loja=d["loja"])
        if d["vendedor"]:
            qs = qs.filter(vendedor=d["vendedor"])

        situacao = d["situacao"]
        if situacao == "pendente":
            qs = qs.pendentes()
        elif situacao == "completo":
            qs = qs.completos()
        elif situacao in dict(LinkPagamento.ETAPAS):
            qs = qs.filter(**{situacao: False})

        if d["q"]:
            qs = qs.filter(Q(cliente__icontains=d["q"]) | Q(nsu__icontains=d["q"]))
        return qs