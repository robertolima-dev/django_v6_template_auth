from django.db import models
from django.conf import settings

from apps.user.models import User


class EmailTemplate(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()  # HTML
    params = models.JSONField(default=dict, blank=True)
    code = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = "Email Template"
        verbose_name_plural = "Email Templates"

    def __str__(self):
        return f"{self.title} ({self.code})"


class EmailUser(models.Model):
    template = models.ForeignKey(EmailTemplate, on_delete=models.CASCADE, related_name="emails")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="emails")
    params = models.JSONField(default=dict, blank=True)
    code = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    sent = models.BooleanField(default=False)
    log = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Email User"
        verbose_name_plural = "Emails Users"
        indexes = [models.Index(fields=["code", "created_at"])]

    def __str__(self):
        return f"{self.code} -> {self.user_id}"
