from django.contrib.auth.forms import AuthenticationForm


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Usuário"
        self.fields["password"].label = "Senha"
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"
        self.fields["username"].widget.attrs["autofocus"] = True