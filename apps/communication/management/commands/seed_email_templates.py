from django.core.management.base import BaseCommand
from django.utils.html import escape

from apps.communication.models import EmailTemplate


CONFIRM_EMAIL_HTML = """
<html>
  <body>
    <h2>Confirme seu e-mail</h2>
    <p>Olá {{ first_name }} {{ last_name }},</p>
    <p>Clique no link abaixo para confirmar o seu e-mail:</p>
    <p><a href="{{ confirm_url }}">Confirmar e-mail</a></p>
    <p>Ou utilize este token: <strong>{{ token }}</strong></p>
  </body>
  </html>
""".strip()


CHANGE_PASSWORD_HTML = """
<html>
  <body>
    <h2>Redefinição de senha</h2>
    <p>Olá {{ first_name }} {{ last_name }},</p>
    <p>Você solicitou a redefinição de senha. Clique no link abaixo:</p>
    <p><a href="{{ reset_url }}">Redefinir senha</a></p>
    <p>Ou utilize este token: <strong>{{ token }}</strong></p>
  </body>
  </html>
""".strip()


class Command(BaseCommand):
    help = "Cria/atualiza templates de e-mail padrões (confirm_email, change_password)"

    def handle(self, *args, **options):
        created_or_updated = []

        confirm, _ = EmailTemplate.objects.update_or_create(
            code="confirm_email",
            defaults={
                "title": "Confirme seu e-mail",
                "content": CONFIRM_EMAIL_HTML,
                "params": {"first_name": "", "last_name": "", "confirm_url": "", "token": ""},
            },
        )
        created_or_updated.append(confirm.code)

        change_pwd, _ = EmailTemplate.objects.update_or_create(
            code="change_password",
            defaults={
                "title": "Redefinição de senha",
                "content": CHANGE_PASSWORD_HTML,
                "params": {"first_name": "", "last_name": "", "reset_url": "", "token": ""},
            },
        )
        created_or_updated.append(change_pwd.code)

        self.stdout.write(self.style.SUCCESS(f"Templates atualizados: {', '.join(created_or_updated)}"))


