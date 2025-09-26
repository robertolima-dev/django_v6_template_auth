from datetime import datetime, timedelta
from datetime import timezone as dt_timezone
from random import randint
from secrets import token_urlsafe
from django.contrib.auth import authenticate, get_user_model
from django.utils import timezone
from django.utils.text import slugify
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from ....services.login_service import LoginService
from ....services.register_service import RegisterService
from ....services.forgot_password_service import ForgotPasswordService
from ....services.reset_password_service import ResetPasswordService
from ....services.confirm_email_service import ConfirmEmailService

from ....models import UserToken

User = get_user_model()


def _issue_access_for_user(user):
    refresh = RefreshToken.for_user(user)
    access = refresh.access_token
    exp = access["exp"]
    now = datetime.now(tz=dt_timezone.utc)
    if isinstance(exp, (int, float)):
        remaining = int(exp - now.timestamp())
    else:
        remaining = int((exp - now).total_seconds()) if hasattr(exp, "__sub__") else 0  # noqa: E501
    if remaining < 0:
        remaining = 0
    return {"token": str(access), "expired_at": remaining}


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        service = LoginService()
        try:
            user = service.login(self.context.get("request"), attrs["email"], attrs["password"])  # noqa: E501
        except Exception as e:
            raise serializers.ValidationError(str(e))
        attrs["user"] = user
        return attrs

    def create(self, validated_data):
        user = validated_data["user"]
        issued = _issue_access_for_user(user)
        return {"user": user, **issued}


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        # username será gerado automaticamente a partir de first_name + last_name + número aleatório  # noqa: E501
        fields = ("email", "first_name", "last_name", "password", "phone", "gender", "date_of_birth")  # noqa: E501

    def create(self, validated_data):
        service = RegisterService()
        try:
            result = service.register(validated_data | {"password": validated_data["password"]})
        except Exception as e:
            raise serializers.ValidationError(str(e))
        user = result["user"]
        issued = _issue_access_for_user(user)
        return {"user": user, "token": result["confirm_token"], "expired_at": result["confirm_expired_at"], **issued}


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def create(self, validated_data):
        try:
            return ForgotPasswordService().forgot_password(validated_data["email"])
        except Exception as e:
            raise serializers.ValidationError(str(e))


class ResetPasswordSerializer(serializers.Serializer):
    token = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        try:
            t = UserToken.objects.get(token=attrs["token"], token_type="change_password")  # noqa: E501
        except UserToken.DoesNotExist:
            raise serializers.ValidationError("Token inválido.")
        if t.expired_at and t.expired_at < timezone.now():
            raise serializers.ValidationError("Token expirado.")
        attrs["user"] = t.user
        attrs["_token_obj"] = t
        return attrs

    def create(self, validated_data):
        try:
            user = ResetPasswordService().reset_password(validated_data["token"], validated_data["password"])
        except Exception as e:
            raise serializers.ValidationError(str(e))
        issued = _issue_access_for_user(user)
        return {"user": user, **issued}


class ConfirmEmailSerializer(serializers.Serializer):
    token = serializers.CharField()

    def validate(self, attrs):
        try:
            t = UserToken.objects.get(token=attrs["token"], token_type="confirm_email")  # noqa: E501
        except UserToken.DoesNotExist:
            raise serializers.ValidationError("Token inválido.")
        if t.expired_at and t.expired_at < timezone.now():
            raise serializers.ValidationError("Token expirado.")
        attrs["user"] = t.user
        attrs["_token_obj"] = t
        return attrs

    def create(self, validated_data):
        try:
            user = ConfirmEmailService().confirm_email(validated_data["token"])
        except Exception as e:
            raise serializers.ValidationError(str(e))
        issued = _issue_access_for_user(user)
        return {"user": user, **issued}
