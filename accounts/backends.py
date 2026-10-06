from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q


class EmailOrUsernameBackend(ModelBackend):
    """
    Allows authentication using either username or email (case-insensitive).
    This enables users to sign in with their Gmail address or their username.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        User = get_user_model()
        if username is None:
            username = kwargs.get("email")
        if not username or not password:
            return None

        clean_identifier = username.strip()
        try:
            user = (
                User.objects.filter(
                    Q(username__iexact=clean_identifier) | Q(email__iexact=clean_identifier)
                )
                .order_by("id")
                .first()
            )
            if user and user.check_password(password) and self.user_can_authenticate(user):
                return user
        except Exception:
            return None

        return None
