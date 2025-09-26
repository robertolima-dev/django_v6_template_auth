import boto3
from botocore.exceptions import BotoCoreError, ClientError
from django.conf import settings

from apps.communication.models import EmailUser
from django.core.mail import EmailMessage



class SendEmailService:
    def handle_email(self, email_user):
        self.send_email(
            email=email_user.user.email,
            subject=email_user.template.title,
            message=email_user.rendered if hasattr(email_user, "rendered") else "",
            instance=email_user,
        )

    def send_email(self, email: str, subject: str, message: str, instance: EmailUser):
        try:
            email_msg = EmailMessage(subject, message, to=[email])
            email_msg.content_subtype = "html"
            email_msg.send()

            instance.sent = True
            instance.save(update_fields=["sent"])

        except Exception as e:
            instance.log = str(e)
            instance.save(update_fields=["log"])
