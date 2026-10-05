from django.shortcuts import redirect
from django.utils.http import url_has_allowed_host_and_scheme


def redirecionar_de_volta(request, padrao):
    """Volta para a página indicada no campo 'proximo' (com os filtros que estavam aplicados).

    Só aceita endereços do próprio sistema; qualquer outro vai para a página padrão.
    """
    destino = request.POST.get("proximo")
    if destino and url_has_allowed_host_and_scheme(
        destino, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        return redirect(destino)
    return redirect(padrao)