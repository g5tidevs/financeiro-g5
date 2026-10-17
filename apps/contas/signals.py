"""Grava no log de acessos cada entrada, saída e tentativa de login que falhou.

O Django avisa esses eventos por "sinais"; aqui só escutamos e registramos.
"""

import logging

from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver

from .models import RegistroAcesso, Usuario

logger = logging.getLogger(__name__)


def _ip(request):
    if request is None:
        return None
    # Atrás do Nginx (na VPS), o IP real do visitante chega no cabeçalho X-Real-IP
    return request.META.get("HTTP_X_REAL_IP") or request.META.get("REMOTE_ADDR") or None


def _navegador(request):
    if request is None:
        return ""
    return request.META.get("HTTP_USER_AGENT", "")[:300]


def _registrar(request, **dados):
    # Um problema no log nunca pode impedir alguém de entrar ou sair
    try:
        RegistroAcesso.objects.create(ip=_ip(request), user_agent=_navegador(request), **dados)
    except Exception:
        logger.exception("Não foi possível gravar o registro de acesso")


@receiver(user_logged_in)
def registrar_entrada(sender, request, user, **kwargs):
    _registrar(request, tipo=RegistroAcesso.Tipo.ENTRADA, usuario=user, username=user.get_username())


@receiver(user_logged_out)
def registrar_saida(sender, request, user, **kwargs):
    if user is None:  # "sair" sem estar logado: nada a registrar
        return
    _registrar(request, tipo=RegistroAcesso.Tipo.SAIDA, usuario=user, username=user.get_username())


@receiver(user_login_failed)
def registrar_falha(sender, credentials, request=None, **kwargs):
    username = (credentials.get("username") or "")[:150]
    usuario = Usuario.objects.filter(username__iexact=username).first() if username else None

    if usuario is None:
        detalhe = "Usuário não existe"
    elif not usuario.is_active:
        detalhe = "Usuário desativado"
    else:
        detalhe = "Senha incorreta"

    _registrar(request, tipo=RegistroAcesso.Tipo.FALHA, usuario=usuario, username=username, detalhe=detalhe)



