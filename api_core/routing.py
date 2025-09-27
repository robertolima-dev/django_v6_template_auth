from django.urls import path
from apps.api.consumers import EchoConsumer

websocket_urlpatterns = [
    path("ws/echo/", EchoConsumer.as_asgi()),
]