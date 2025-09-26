from datetime import timedelta
from random import randint

from django.utils import timezone
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from secrets import token_urlsafe

from apps.communication.models import EmailTemplate, EmailUser
from ..models import UserToken


User = get_user_model()


class RegisterService:
    def register(self, data: dict):
        required = ["email", "first_name", "last_name", "password"]
        for field in required:
            if not data.get(field):
                raise Exception(f"Campo obrigatório ausente: {field}")

        email = data["email"]
        if User.objects.filter(email__iexact=email).exists():
            raise Exception("E-mail já cadastrado.")

        base = slugify(f"{data.get('first_name', '')}_{data.get('last_name', '')}") or "user"
        username = None
        for _ in range(1000):
            candidate = f"{base}_{randint(0, 999)}"
            if not User.objects.filter(username__iexact=candidate).exists():
                username = candidate
                break
        if username is None:
            username = f"{base}_{int(timezone.now().timestamp())}"

        user = User(
            username=username,
            email=email,
            first_name=data.get("first_name", ""),
            last_name=data.get("last_name", ""),
            phone=data.get("phone", ""),
            gender=data.get("gender", ""),
            date_of_birth=data.get("date_of_birth"),
        )
        user.set_password(data["password"])
        user.save()

        confirm = UserToken.objects.create(
            token=self._generate_token(),
            user=user,
            token_type="confirm_email",
            expired_at=timezone.now() + timedelta(days=1),
        )

        template = EmailTemplate.objects.filter(code="confirm_email").first()
        if template:
            params = {
                "first_name": user.first_name,
                "last_name": user.last_name,
                "confirm_url": "",
                "token": confirm.token,
            }
            EmailUser.objects.create(
                template=template,
                user=user,
                code="confirm_email",
                params=params,
            )

        return {"user": user, "confirm_token": confirm.token, "confirm_expired_at": confirm.expired_at}

    def _generate_token(self) -> str:
        return token_urlsafe(30)[:40]
