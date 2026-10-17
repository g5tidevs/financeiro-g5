from django.contrib.auth.forms import AuthenticationForm, SetPasswordForm, UserCreationForm
from django.db.models import Q

from apps.cadastros.models import Loja
from apps.core.forms import BootstrapFormMixin, BootstrapModelForm

from .models import Usuario

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