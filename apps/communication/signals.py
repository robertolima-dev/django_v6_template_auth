from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template import Template, Context

from .models import EmailUser, EmailTemplate
from .services.send_email_service import SendEmailService


@receiver(post_save, sender=EmailUser)
def send_email_on_create(sender, instance: EmailUser, created: bool, **kwargs):
    if not created:
        return

    try:
        template = EmailTemplate.objects.get(code=instance.code)
    except EmailTemplate.DoesNotExist:
        return

    # merge de params: do template e do EmailUser, priorizando do EmailUser
    params = {**(template.params or {}), **(instance.params or {})}
    subject = template.title
    html_template = Template(template.content)
    html_content = html_template.render(Context(params))
    # anexar conteúdo renderizado na instância para o service
    setattr(instance, "rendered", html_content)

    service = SendEmailService()
    service.handle_email(instance)
