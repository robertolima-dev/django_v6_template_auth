from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

GENDER_CHOICES = (
    ("m", "m"),
    ("f", "f"),
    ("o", "o"),
)

TYPE_CHOICES = (
    ("confirm_email", "confirm_email"),
    ("unsubscribe", "unsubscribe"),
    ("change_password", "change_password"),
)


class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    confirm_email = models.BooleanField(default=False)
    unsubscribe = models.BooleanField(default=False)

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return f'{self.username} - {self.email}'


class UserToken(models.Model):
    token = models.CharField(_("Key"), max_length=40, primary_key=True, db_index=True)  # noqa: E501
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="tokens")  # noqa: E501
    token_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    expired_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "User Token"
        verbose_name_plural = "User Tokens"
        indexes = [
            models.Index(fields=["token_type"]),
            models.Index(fields=["expired_at"]),
        ]

    def __str__(self):
        return f"{self.token_type}:{self.token}"
