"""
ASGI config for port_ocpp project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/asgi/
"""

import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
import Controller.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'port_ocpp.settings')

#application = get_asgi_application()
application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    #"websocket": AuthMiddlewareStack(URLRouter(app_ocpp.routing.websocket_urlpatterns)),
    # Just HTTP for now. (We can add other protocols later.)
    "websocket": AuthMiddlewareStack(
        URLRouter(
            Controller.routing.websocket_urlpatterns
        )
    ),
})
