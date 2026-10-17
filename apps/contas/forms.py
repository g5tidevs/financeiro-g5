from django.contrib.auth.forms import AuthenticationForm, SetPasswordForm, UserCreationForm
from django.db.models import Q
from django import forms
from apps.cadastros.models import Loja
from apps.core.forms import BootstrapFormMixin, BootstrapModelForm

from .models import RegistroAcesso, Usuario

ROTULOS = {
    "username": "Usuário (login)",
    "first_name": "Nome",
    "last_name": "Sobrenome",
    "email": "E-mail",
}


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Usuário"
        self.fields["password"].label = "Senha"
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"
        self.fields["username"].widget.attrs["autofocus"] = True


class UsuarioCriarForm(BootstrapFormMixin, UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Usuario
        fields = ("first_name", "last_name", "username", "email", "papel", "loja")
        labels = ROTULOS
        help_texts = {"username": "É o que a pessoa digita para entrar. Sem espaços nem acentos."}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["first_name"].required = True
        self.fields["loja"].queryset = Loja.objects.ativos()
        self.fields["password1"].label = "Senha"
        self.fields["password2"].label = "Confirme a senha"
        self.fields["password2"].help_text = "Digite a mesma senha de novo."


class UsuarioEditarForm(BootstrapModelForm):
    class Meta:
        model = Usuario
        fields = ("first_name", "last_name", "username", "email", "papel", "loja")
        labels = ROTULOS
        help_texts = {"username": "É o que a pessoa digita para entrar. Sem espaços nem acentos."}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["first_name"].required = True
        self.fields["loja"].queryset = Loja.objects.filter(Q(ativo=True) | Q(pk=self.instance.loja_id))

    def clean_username(self):
        # O login não diferencia maiúsculas, então "Marcos" e "marcos" seriam a mesma pessoa
        username = self.cleaned_data["username"]
        if Usuario.objects.filter(username__iexact=username).exclude(pk=self.instance.pk).exists():
            raise self.instance.unique_error_message(Usuario, ["username"])
        return username


class UsuarioSenhaForm(BootstrapFormMixin, SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["new_password1"].label = "Nova senha"
        self.fields["new_password2"].label = "Confirme a nova senha"


class AcessoFiltroForm(BootstrapFormMixin, forms.Form):
    TIPOS = [("", "Todos")] + list(RegistroAcesso.Tipo.choices)

    inicio = forms.DateField(label="De", required=False,
                             widget=forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}))
    fim = forms.DateField(label="Até", required=False,
                          widget=forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}))
    tipo = forms.ChoiceField(label="Evento", choices=TIPOS, required=False)
    q = forms.CharField(
        label="Buscar", required=False,
        widget=forms.TextInput(attrs={"type": "search", "placeholder": "Usuário ou IP"}),
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
            qs = qs.filter(data_hora__date__gte=d["inicio"])
        if d["fim"]:
            qs = qs.filter(data_hora__date__lte=d["fim"])
        if d["tipo"]:
            qs = qs.filter(tipo=d["tipo"])
        if d["q"]:
            qs = qs.filter(
                Q(username__icontains=d["q"])
                | Q(usuario__first_name__icontains=d["q"])
                | Q(usuario__last_name__icontains=d["q"])
                | Q(ip__startswith=d["q"])
            )
        return qs        