from functools import wraps

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden


def shop_admin_required(view_func):
    @login_required
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not getattr(request.user, "is_shop_admin", False):
            return HttpResponseForbidden("Admin access required.")
        return view_func(request, *args, **kwargs)

    return _wrapped
