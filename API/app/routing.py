'''
En esta seccion mantendremos las rutas websokets que corren pordebajo del api
In this section  runs de urls websockets, under the API
'''

from django.urls import re_path

from . import consumers


websocket_urlpatterns = [
    #re_path(r'ws/chat/(?P<room_name>\w+)/$', consumers.ChatConsumer.as_asgi()),
    #re_path('ws/chat/prueba/', consumers.ChatConsumer.as_asgi()),
    re_path('ws/chat/prueba/', consumers.ChargePoint.as_asgi()),
]