from django import forms

from apps.cadastros.models import Loja
from apps.core.forms import BootstrapFormMixin

CAMPO_DATA = forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"})


class DashboardFiltroForm(BootstrapFormMixin, forms.Form):
    DIAS = [("3", "3 dias"), ("7", "7 dias"), ("15", "15 dias"), ("30", "30 dias")]

    inicio = forms.DateField(label="De", widget=CAMPO_DATA)
    fim = forms.DateField(label="Até", widget=CAMPO_DATA)
    loja = forms.ModelChoiceField(label="Loja", queryset=Loja.objects.all(), required=False, empty_label="Todas")
    dias = forms.TypedChoiceField(label="Parado há mais de", choices=DIAS, coerce=int)

    def clean(self):
        dados = super().clean()
        inicio, fim = dados.get("inicio"), dados.get("fim")
        if inicio and fim and inicio > fim:
            raise forms.ValidationError("A data inicial não pode ser depois da data final.")
        return dados