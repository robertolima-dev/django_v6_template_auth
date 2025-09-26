from rest_framework import serializers
from apps.user.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"


class UserMeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ("groups", "user_permissions")
