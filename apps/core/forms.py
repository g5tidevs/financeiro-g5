from decimal import Decimal

from django import forms


class BootstrapFormMixin:
    """Aplica as classes do Bootstrap em todos os campos do formulário."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, forms.CheckboxInput):
                classe = "form-check-input"
            elif isinstance(widget, (forms.Select, forms.SelectMultiple)):
                classe = "form-select"
            else:
                classe = "form-control"
            widget.attrs["class"] = classe

    def full_clean(self):
        super().full_clean()
        # Marca em vermelho os campos que têm erro
        for nome in self.errors:
            if nome in self.fields:
                widget = self.fields[nome].widget
                widget.attrs["class"] = widget.attrs.get("class", "") + " is-invalid"


class BootstrapModelForm(BootstrapFormMixin, forms.ModelForm):
    pass


class ValorBRField(forms.DecimalField):
    """Campo de dinheiro no formato brasileiro.

    Aceita: 150 | 150,5 | 1.234,56 | 1234.56 | R$ 1.234,56
    """

    widget = forms.TextInput

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("max_digits", 12)
        kwargs.setdefault("decimal_places", 2)
        kwargs.setdefault("min_value", Decimal("0.01"))
        super().__init__(*args, **kwargs)

    def widget_attrs(self, widget):
        attrs = super().widget_attrs(widget)
        attrs["inputmode"] = "decimal"
        attrs["placeholder"] = "0,00"
        return attrs

    def to_python(self, value):
        if isinstance(value, str):
            value = value.replace("R$", "").replace(" ", "").strip()
            if "," in value:
                value = value.replace(".", "").replace(",", ".")
        return super().to_python(value)

    def prepare_value(self, value):
        if isinstance(value, Decimal):
            return f"{value:.2f}".replace(".", ",")
        return value