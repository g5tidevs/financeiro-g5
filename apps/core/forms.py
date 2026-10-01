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