from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from apps.user.api.v1.auth.viewsets import AuthViewSet
from apps.user.api.v1.user.viewsets import UserViewSet

router = DefaultRouter()
router.register(r"auth", AuthViewSet, basename="auth")
router.register(r"users", UserViewSet, basename="users")

urlpatterns = [
    path("health/", views.health, name="api-health"),
    path("", include(router.urls)),
]
