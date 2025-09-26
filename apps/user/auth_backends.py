from typing import Optional

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

User = get_user_model()


class EmailOrUsernameBackend(ModelBackend):
    def authenticate(self, request, username: Optional[str] = None, password: Optional[str] = None, **kwargs):  # noqa: E501
        login = username or kwargs.get("email")
        if not login or not password:
            return None
        try:
            user = User.objects.get(Q(username__iexact=login) | Q(email__iexact=login))  # noqa: E501
        except User.DoesNotExist:
            return None
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
