import json
from channels.generic.websocket import WebsocketConsumer

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