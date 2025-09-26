from django.utils import timezone
from django.contrib.auth import get_user_model
from ..models import UserToken


User = get_user_model()


class ResetPasswordService:
    def reset_password(self, token: str, password: str):
        if not token or not password:
            raise Exception("Token e nova senha são obrigatórios.")
        try:
            t = UserToken.objects.get(token=token, token_type="change_password")
        except UserToken.DoesNotExist:
            raise Exception("Token inválido.")
        if t.expired_at and t.expired_at < timezone.now():
            raise Exception("Token expirado.")
        user = t.user
        user.set_password(password)
        user.save(update_fields=["password"])
        t.delete()
        return user
