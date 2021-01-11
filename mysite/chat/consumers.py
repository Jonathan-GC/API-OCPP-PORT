import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer


'''##Esta arte funciona muy bien sin docker
    class ChatConsumer(WebsocketConsumer):
        def connect(self):
            self.accept()

        def disconnect(self, close_code):
            pass

        def receive(self, text_data):
            try:
                text_data_json = json.loads(text_data)
                message = text_data_json["message"]
                print(f"> {message}")
                texto2 = json.dumps({"message": message })
                self.send(texto2)
            except:
                text_data_json = json.loads(text_data)
                id_tag = text_data_json[1]

                texto2 = json.dumps([3, id_tag , {"currentTime": "2019-06-16T11:18:09.591716", "interval": 10, "status": "Accepted"}])
                self.send(texto2)
'''

'''##Esta arte funciona muy bien con docker
    class ChatConsumer(WebsocketConsumer):
        def connect(self):
            self.room_name = self.scope['url_route']['kwargs']['room_name']
            self.room_group_name = 'chat_%s' % self.room_name

            # Join room group
            async_to_sync(self.channel_layer.group_add)(
                self.room_group_name,
                self.channel_name
            )

            self.accept()

        def disconnect(self, close_code):
            # Leave room group
            async_to_sync(self.channel_layer.group_discard)(
                self.room_group_name,
                self.channel_name
            )

        # Receive message from WebSocket
        def receive(self, text_data):
            text_data_json = json.loads(text_data)
            message = text_data_json['message']

            # Send message to room group
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message
                }
            )

        # Receive message from room group
        def chat_message(self, event):
            message = event['message']

            # Send message to WebSocket
            self.send(text_data=json.dumps({
                'message': message
            }))
'''