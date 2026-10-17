from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


class LoginSemMaiusculasBackend(ModelBackend):
    """Login que não diferencia maiúsculas no usuário: "Marcos", "marcos" e "MARCOS" entram na mesma conta.
    A senha continua diferenciando."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        Usuario = get_user_model()
        if username is None:
            username = kwargs.get(Usuario.USERNAME_FIELD)
        if username is None or password is None:
            return None

        # A grafia exata vem primeiro: contas antigas que só diferem nas maiúsculas continuam entrando cada uma na sua
        usuario = Usuario._default_manager.filter(username=username).first()
        if usuario is None:
            encontrados = list(Usuario._default_manager.filter(username__iexact=username)[:2])
            if len(encontrados) != 1:
                # Nenhuma conta, ou mais de uma e não dá para saber qual. Calcula um hash à toa para a resposta
                # demorar o mesmo que um login válido e não revelar se o usuário existe (como faz o ModelBackend).
                Usuario().set_password(password)
                return None
            usuario = encontrados[0]

        if usuario.check_password(password) and self.user_can_authenticate(usuario):
            return usuario
        return None
