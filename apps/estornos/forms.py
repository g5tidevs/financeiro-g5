from django import forms
from django.db.models import Count, Q
from django.utils import timezone

from apps.cadastros.models import Loja
from apps.core.forms import BootstrapFormMixin, BootstrapModelForm, ValorBRField

from .models import EstornoCartao

CAMPO_DATA = forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"})


class EstornoCartaoForm(BootstrapModelForm):
    valor = ValorBRField(label="Valor")
    confirmar_nsu = forms.BooleanField(
        label="Confirmo que é outro estorno da mesma venda (ex.: estorno parcial)",
        required=False,
    )

    class Meta:
        model = EstornoCartao
        fields = [
            "data", "loja", "cliente", "contato_cliente", "data_venda", "valor",
            "nsu", "motivo", "solicitado_banco", "conciliado",
        ]
        widgets = {
            "data": CAMPO_DATA,
            "data_venda": CAMPO_DATA,
            "nsu": forms.TextInput(attrs={"inputmode": "numeric", "autocomplete": "off"}),
            "motivo": forms.TextInput(attrs={"list": "motivos-sugeridos", "autocomplete": "off"}),
        }

    def __init__(self, *args, usuario=None, **kwargs):
        super().__init__(*args, **kwargs)
        inst = self.instance
        self.estorno_mesmo_nsu = None  # preenchido se o NSU já tiver estorno

        self.fields["loja"].queryset = Loja.objects.filter(Q(ativo=True) | Q(pk=inst.loja_id))

        if not inst.pk:
            self.fields["data"].initial = timezone.localdate()
            if usuario and usuario.loja_id:
                self.fields["loja"].initial = usuario.loja_id

    def sugestoes_motivo(self):
        """Os 30 motivos mais usados, para sugerir enquanto o usuário digita."""
        return (
            EstornoCartao.objects.ativos()
            .values_list("motivo", flat=True)
            .annotate(usos=Count("id"))
            .order_by("-usos", "motivo")[:30]
        )

    def clean_nsu(self):
        # Aceita o NSU colado com espaços, pontos ou traços
        nsu = self.cleaned_data["nsu"]
        return "".join(c for c in nsu if c.isdigit()) or nsu.strip()

    def clean_motivo(self):
        motivo = " ".join(self.cleaned_data["motivo"].split())
        return motivo[:1].upper() + motivo[1:]

    def clean(self):
        dados = super().clean()
        nsu = dados.get("nsu")
        nsu_mudou = nsu != self.instance.nsu  # ao editar, só confere se o NSU foi alterado
        if nsu and nsu_mudou:
            repetido = (
                EstornoCartao.objects.ativos()
                .filter(nsu=nsu)
                .exclude(pk=self.instance.pk)
                .first()
            )
            if repetido and not dados.get("confirmar_nsu"):
                self.estorno_mesmo_nsu = repetido
                self.add_error(
                    "nsu",
                    f"Já existe um estorno com este NSU: {repetido.cliente}, "
                    f"lançado em {repetido.data:%d/%m/%Y}. Confira para não estornar duas vezes.",
                )
        return dados


class EstornoFiltroForm(BootstrapFormMixin, forms.Form):
    SIM_NAO = [("", "Todos"), ("nao", "Pendentes"), ("sim", "Feitos")]

    inicio = forms.DateField(label="De", required=False, widget=CAMPO_DATA)
    fim = forms.DateField(label="Até", required=False, widget=CAMPO_DATA)
    loja = forms.ModelChoiceField(label="Loja", queryset=Loja.objects.all(), required=False, empty_label="Todas")
    safra = forms.ChoiceField(label="Safra", choices=SIM_NAO, required=False)
    ejl = forms.ChoiceField(label="EJL", choices=SIM_NAO, required=False)
    q = forms.CharField(
        label="Buscar", required=False,
        widget=forms.TextInput(attrs={"type": "search", "placeholder": "Cliente, NSU, motivo ou contato"}),
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
            qs = qs.filter(loja=d["loja"])
        if d["safra"]:
            qs = qs.filter(solicitado_banco=(d["safra"] == "sim"))
        if d["ejl"]:
            qs = qs.filter(conciliado=(d["ejl"] == "sim"))
        if d["q"]:
            qs = qs.filter(
                Q(cliente__icontains=d["q"])
                | Q(nsu__icontains=d["q"])
                | Q(motivo__icontains=d["q"])
                | Q(contato_cliente__icontains=d["q"])
            )
        return qs