from datetime import timedelta
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.conf import settings
from apps.communication.models import EmailTemplate, EmailUser
from ..models import UserToken
from secrets import token_urlsafe

User = get_user_model()


class ForgotPasswordService:
    def forgot_password(self, email: str) -> dict:
        if not email:
            raise Exception("E-mail é obrigatório.")
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return {"sent": True}
        token = UserToken.objects.create(
            token=self._generate_token(),
            user=user,
            token_type="change_password",
            expired_at=timezone.now() + timedelta(hours=1),
        )
        # Criar EmailUser com params prontos (signal ignora envio para change_password)
        template = EmailTemplate.objects.filter(code="change_password").first()
        if template:
            reset_base = getattr(settings, "FRONTEND_RESET_PASSWORD_URL", "")
            params = {
                "first_name": user.first_name,
                "last_name": user.last_name,
                "reset_url": f"{reset_base}{token.token}" if reset_base else "",
                "token": token.token,
            }
            EmailUser.objects.create(
                template=template,
                user=user,
                code="change_password",
                params=params,
            )
        return {"sent": True, "token": token.token, "expired_at": token.expired_at}

    def _generate_token(self) -> str:
        return token_urlsafe(30)[:40]