"""
ASGI config for api_core project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/dev/howto/deployment/asgi/
"""

# import os

# from django.core.asgi import get_asgi_application

# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "api_core.settings.dev")

# application = get_asgi_application()


import os
from django.core.asgi import get_asgi_application
from django.conf import settings
from django.contrib.staticfiles.handlers import ASGIStaticFilesHandler
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import api_core.routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "api_core.settings.dev")

django_asgi_app = get_asgi_application()

# Serve static files in DEBUG when using ASGI servers (Daphne/Uvicorn)
http_app = ASGIStaticFilesHandler(django_asgi_app) if settings.DEBUG else django_asgi_app

application = ProtocolTypeRouter({
    "http": http_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(api_core.routing.websocket_urlpatterns)
    ),
})