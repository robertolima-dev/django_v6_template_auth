from django.utils import timezone
from django.contrib.auth import get_user_model
from ..models import UserToken


User = get_user_model()


class ConfirmEmailService:
    def confirm_email(self, token: str):
        if not token:
            raise Exception("Token é obrigatório.")
        try:
            t = UserToken.objects.get(token=token, token_type="confirm_email")
        except UserToken.DoesNotExist:
            raise Exception("Token inválido.")
        if t.expired_at and t.expired_at < timezone.now():
            raise Exception("Token expirado.")
        user = t.user
        user.confirm_email = True
        user.save(update_fields=["confirm_email"])
        t.delete()
        return user