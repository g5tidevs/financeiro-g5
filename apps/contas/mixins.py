from functools import wraps

from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied


class SupervisorRequiredMixin(UserPassesTestMixin):
    """Para views em classe: só supervisores acessam. Os demais recebem erro 403."""

    def test_func(self):
        user = self.request.user
        return user.is_authenticated and user.is_supervisor


def supervisor_required(view_func):
    """Para views em função."""

    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not (request.user.is_authenticated and request.user.is_supervisor):
            raise PermissionDenied
        return view_func(request, *args, **kwargs)

    return _wrapped