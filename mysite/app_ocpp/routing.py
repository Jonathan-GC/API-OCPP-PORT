# chat/routing.py
from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<room_name>\w+)/$', consumers.ChatConsumer.as_asgi()),
    #re_path(r'ws/chat/(?P<room_name>\w+)/saludo/$', consumers.ChatConsumer.as_asgi()),
    re_path(r'ws/charger/(?P<chager_name>\w+)/$', consumers.Charger().as_asgi()),

    
]