import json
#from asgiref.sync import async_to_sync
#from channels.generic.websocket import WebsocketConsumer
from channels.generic.websocket import AsyncWebsocketConsumer
import logging
from datetime import datetime

from ocpp.routing import on, after
from ocpp.v16 import ChargePoint as cp
from ocpp.v16.enums import Action, RegistrationStatus, AuthorizationStatus
from ocpp.v16 import call_result

logging.basicConfig(level=logging.INFO)

class ChargePoint(cp, AsyncWebsocketConsumer):
    
    async def connect(self):
        await self.accept()


    #Decorador principal de pedido clientes 
    @on(Action.BootNotification)
    def on_boot_notitication(self, charge_point_vendor: str, charge_point_model: str, **kwargs):
        return call_result.BootNotificationPayload(
            current_time=datetime.utcnow().isoformat(),
            interval=10,
            status=RegistrationStatus.accepted
        )


    #Decorador posterior a la aceptacion del cliente
    @after(Action.BootNotification)
    def after_boot_notification(self, charge_point_vendor: str, charge_point_model: str, **kwargs):
        print("Conexion Mongo o SQL y verificaciones del sistema")

    
    try:
        @on(Action.Authorize)
        def on_authorize_response(self, id_tag: str):
            print("He recibido: ", id_tag)
            
            return call_result.AuthorizePayload(
                id_tag_info={
                    "status" : AuthorizationStatus.accepted
                }
            )
            
    except: 
        print("No se puede hacer la transaccion")
    
    
    @on(Action.StartTransaction)
    def on_start_transaction(self, connector_id: int, id_tag: str, meter_start: int, timestamp: str, **kwargs):
        return call_result.StartTransactionPayload(
            transaction_id=connector_id,
            id_tag_info={
                "status" : AuthorizationStatus.accepted
            }
        )

    @after(Action.StartTransaction)
    def imprimirJoder(self, connector_id: int, id_tag: str, meter_start: int, timestamp: str, **kwargs):
        print("dispensado de energia ", meter_start, "units")


    @on(Action.StopTransaction)
    def on_stop_transaction(self, transaction_id: int, timestamp: str, meter_stop: int):
        return call_result.StopTransactionPayload(
            id_tag_info={
                "status" : AuthorizationStatus.accepted
            }
        )

    @after(Action.StopTransaction)
    def imprimir(self, transaction_id: int, timestamp: str, meter_stop: int):
        print("Deteniendo Transaccion en", meter_stop, "units recargadas")
    

    @on(Action.Heartbeat)
    def on_heartbeat(self):
        return call_result.HeartbeatPayload(
            current_time=datetime.utcnow().isoformat()
        )
    
    @after(Action.Heartbeat)
    def imprimirMenssage(self):
        print("tomando Pulso del cargador")


    @on(Action.StatusNotification)
    def on_status_notification(self, connector_id: int, error_code: str, status: str, timestamp: str, info: str, vendor_id: str, vendor_error_code: str):
        return call_result.StatusNotificationPayload(

        )
    
    @after(Action.StatusNotification)
    def imprimirMenssage(self, connector_id: int, error_code: str, status: str, timestamp: str, info: str, vendor_id: str, vendor_error_code: str):
        print("tomando Pulso del cargador")

#async def on_connect(AsyncWebsocketConsumer, path):
#    charge_point_id = path.strip('/')
#    cp = ChargePoint(charge_point_id, AsyncWebsocketConsumer)
#
#    await cp.start()
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
'''
    class ChatConsumer(AsyncWebsocketConsumer):
        async def connect(self):
            self.room_name = self.scope['url_route']['kwargs']['room_name']
            self.room_group_name = 'chat_%s' % self.room_name

            # Join room group
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

            await self.accept()

        async def disconnect(self, close_code):
            # Leave room group
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

        
        # Receive message from WebSocket
        async def receive(self, text_data):
            text_data_json = json.loads(text_data)
            message = text_data_json['message']

            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message
                }
            )

        
        # Receive message from room group
        async def chat_message(self, event):
            message = event['message']

            # Send message to WebSocket
            await self.send(text_data=json.dumps({
                'message': message
            }))
'''

