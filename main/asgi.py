import os

from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import re_path as url
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "main.settings")
# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.
django_asgi_app = get_asgi_application()

from channels.auth import AuthMiddlewareStack
from main.consumers import NotificationConsumer

application = ProtocolTypeRouter({
    # Django's ASGI application to handle traditional HTTP requests
    "http": django_asgi_app,

    # WebSocket chat handler
    "websocket": AuthMiddlewareStack(
        URLRouter([
            url(r'ws/notifications', NotificationConsumer.as_asgi()),
        ])
    ),
})
