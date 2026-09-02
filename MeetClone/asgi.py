import os

from django.core.asgi import get_asgi_application


# =========================================================
# DJANGO SETTINGS
# =========================================================

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "MeetClone.settings"
)


# =========================================================
# INITIALIZE DJANGO FIRST
# =========================================================

django_asgi_app = get_asgi_application()


# =========================================================
# IMPORT CHANNELS AFTER DJANGO INITIALIZATION
# =========================================================

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter

from meetings.routing import websocket_urlpatterns


# =========================================================
# ASGI APPLICATION
# =========================================================

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,

        "websocket": AuthMiddlewareStack(
            URLRouter(
                websocket_urlpatterns
            )
        ),
    }
)