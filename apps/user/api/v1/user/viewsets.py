from datetime import datetime, timezone as dt_timezone
from django.utils import timezone
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserSerializer, UserMeSerializer
from apps.user.models import User


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(id=self.request.user.id)

    @action(methods=["get"], detail=False, permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        user = request.user
        # Reuse the same JWT from the header and compute its expiration
        token_str = request.META.get("HTTP_AUTHORIZATION", "").split(" ")[-1]
        validated = request.auth  # provided by JWTAuthentication
        exp = validated["exp"]
        now = datetime.now(tz=dt_timezone.utc)
        if isinstance(exp, (int, float)):
            expired_at = int(exp - now.timestamp())
        else:
            expired_at = int((exp - now).total_seconds()) if hasattr(exp, "__sub__") else 0
        if expired_at < 0:
            expired_at = 0
        return Response({
            "user": UserMeSerializer(user).data,
            "token": token_str,
            "expired_at": expired_at,
        })
