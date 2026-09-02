import os

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "MeetClone.settings"
)

from django.core.asgi import get_asgi_application

# Django ko pehle initialize karo
django_asgi_app = get_asgi_application()

# Django initialize hone ke BAAD routing import karo
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter

from meetings.routing import websocket_urlpatterns


application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,

        "websocket": AuthMiddlewareStack(
            URLRouter(websocket_urlpatterns)
        ),
    }
)