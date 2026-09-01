"""
ASGI config for MeetClone project.
"""

import os

from django.core.asgi import get_asgi_application

from channels.auth import AuthMiddlewareStack

from channels.routing import (
    ProtocolTypeRouter,
    URLRouter,
)

from django.contrib.staticfiles.handlers import ASGIStaticFilesHandler

from meetings.routing import (
    websocket_urlpatterns,
)


os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "MeetClone.settings"
)


django_asgi_app = (
    get_asgi_application()
)


application = ProtocolTypeRouter({

    "http":
        ASGIStaticFilesHandler(
            django_asgi_app
        ),

    "websocket":
        AuthMiddlewareStack(

            URLRouter(
                websocket_urlpatterns
            )

        ),

})