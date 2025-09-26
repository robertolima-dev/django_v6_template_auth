from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.user.api.v1.user.serializers import UserMeSerializer

from .serializers import (ConfirmEmailSerializer, ForgotPasswordSerializer,
                          LoginSerializer, RegisterSerializer,
                          ResetPasswordSerializer)


class AuthViewSet(viewsets.GenericViewSet):
    @action(methods=["post"], detail=False)
    def login(self, request):
        serializer = LoginSerializer(data=request.data, context={"request": request})  # noqa: E501
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        data = {"user": UserMeSerializer(result["user"]).data, "token": result["token"], "expired_at": result["expired_at"]}  # noqa: E501
        return Response(data)

    @action(methods=["post"], detail=False)
    def register(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        data = {"user": UserMeSerializer(result["user"]).data, "token": result["token"], "expired_at": result["expired_at"]}  # noqa: E501
        return Response(data, status=status.HTTP_201_CREATED)

    @action(methods=["post"], detail=False)
    def forgot_password(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {'message': 'Email enviado com sucesso'},
            status=status.HTTP_200_OK
        )

    @action(methods=["post"], detail=False)
    def reset_password(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        data = {"user": UserMeSerializer(result["user"]).data, "token": result["token"], "expired_at": result["expired_at"]}  # noqa: E501
        return Response(data)

    @action(methods=["post"], detail=False)
    def confirm_email(self, request):
        serializer = ConfirmEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        data = {"user": UserMeSerializer(result["user"]).data, "token": result["token"], "expired_at": result["expired_at"]}  # noqa: E501
        return Response(data)

    def _user_data(self, user):
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "phone": getattr(user, "phone", ""),
            "gender": getattr(user, "gender", ""),
            "date_of_birth": getattr(user, "date_of_birth", None),
        }
