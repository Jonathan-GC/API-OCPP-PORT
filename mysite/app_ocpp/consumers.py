# chat/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer

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

            print(self.channel_name)
            print(self.room_group_name)

            await self.accept()

        async def disconnect(self, close_code):
            print(close_code)
            # Leave room group
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
        
        # Receive message from WebSocket
        async def receive(self, text_data):
            text_data_json = json.loads(text_data)
            message = text_data_json['message']
            print(message)
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
            print("mensaje del grupo: " + message)
            # Send message to WebSocket
            await self.send(text_data=json.dumps({
                'message': message
            }))

        def pruebaFunc(joder):
            print("hola mundo")
'''    
import uuid
import logging
from datetime import datetime
import asyncio
from ocpp.routing import on, after
from ocpp.v16 import ChargePoint as cp
from ocpp.v16 import Prueba
from ocpp.v16.enums import Action, RegistrationStatus, AuthorizationStatus, RemoteStartStopStatus
from ocpp.v16 import call_result, call

from channels.layers import get_channel_layer
from channels.consumer import SyncConsumer

logging.basicConfig(level=logging.INFO)


cargadoresOnline = []

class ActionCharger:
    @on(Action.BootNotification)
    def on_boot_notification(self, charge_point_vendor: str, charge_point_model: str, **kwargs):
        return call_result.BootNotificationPayload(
            current_time=datetime.utcnow().isoformat(),
            interval=10,
            status=RegistrationStatus.accepted
        )

    @after(Action.BootNotification)
    def after_boot_notification(self, charge_point_vendor: str, charge_point_model: str, **kwargs):
        print("Estoy en el after")

    try:
        @on(Action.Authorize)
        def on_authorize_response(self, id_tag: str, **kwargs):
            self.idTag = id_tag
            
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
        print("Otras medidas: ", **kwargs)


    @on(Action.StopTransaction)
    def on_stop_transaction(self, transaction_id: int, timestamp: str, meter_stop: int, **kwargs):
        return call_result.StopTransactionPayload(
            id_tag_info={
                "status" : AuthorizationStatus.accepted
            }
        )

    @after(Action.StopTransaction)
    def imprimir(self, transaction_id: int, timestamp: str, meter_stop: int, **kwargs):
        print("Deteniendo Transaccion en", meter_stop, "units recargadas", "id de transaccion: ", transaction_id)
    

    @on(Action.Heartbeat)
    def on_heartbeat(self, **kwargs):
        return call_result.HeartbeatPayload(
            current_time=datetime.utcnow().isoformat()
        )
    
    @after(Action.Heartbeat)
    def imprimirMenssage(self):
        print("tomando Pulso del cargador")


    @on(Action.StatusNotification)
    def on_status_notification(self, connector_id: int, error_code: str, status: str, timestamp: str, info: str, vendor_id: str, vendor_error_code: str, **kwargs):
        self.idConector = connector_id
        return call_result.StatusNotificationPayload(

        )
    
    @after(Action.StatusNotification)
    def imprimirMenssage(self, connector_id: int, error_code: str, status: str, timestamp: str, info: str, vendor_id: str, vendor_error_code: str, **kwargs):
        print("tomando Pulso del cargador")

    @on(Action.MeterValues)
    def on_meter_values (self, connector_id: int, **kwargs):
        return call_result.MeterValuesPayload(
            
        )



    async def stop_charge_remote(self):
        
        print("Detener orden de carga remota")
        msn= call.RemoteStopTransactionPayload(
            transaction_id = 12
        )
        response = await self.call(msn)
        

    async def start_charge_remote(self):
        print("Iniciar orden de carga remota")
        msn = call.RemoteStartTransactionPayload(
            id_tag = str(self.idTag),
            connector_id = self.idConector       
            )

        response = await self.call(msn)

class Charger (cp, ActionCharger):

    """
    This the point start to connect a client charger, here are set the variables
    of connection importants.

        self.charger_name   --> Received from URL  
        self.idTag          --> Received from Authorize function  
        self.idConector     --> Received from status notification function 
    """
    
    def __init__(self, name = "", **kwds):
        
        self.charger_name = name
        self.idTag = None
        self.idConector = None

        super().__init__()
        

    async def connect(self):
        self.charger_name = self.scope['url_route']['kwargs']['chager_name']
        self.room_charger_controller = 'charger_contorller_%s' % self.charger_name
        
        # Join room charger controller
        await self.channel_layer.group_add(
            self.room_charger_controller,
            self.channel_name
        )

        response = await super().connect(self.charger_name)



        if response is "201":
            cargador = dict(
                charger_name = self.charger_name,
                controller = self.room_charger_controller
                )

            cargadoresOnline.append(cargador)


    async def disconnect(self, close_code):
        # leave room charger controller
        await self.channel_layer.group_discard(
            self.room_charger_controller,
            self.channel_name
        )

    async def receive(self, text_data):
        #Esto es temporal y es para probar solamente la StopTransaction
        if text_data == "s":
            await self.stop_charge_remote()
        else:
            await super().start(text_data)

    # Receive message from room controller
    async def control_message(self, event):
        message = event['message']
        # Send message to WebSocket
        if message == "s":
            await self.start_charge_remote()
        if message == "n":
            await self.stop_charge_remote()

class ChatConsumer(AsyncWebsocketConsumer):
    
    
        

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        canal.append(self.channel_name)
        Grupo.append(self.room_group_name)
        print("Group Name: ", self.room_group_name)
        print("channel Name: ", self.channel_name)

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
                'type': 'control_message',
                'message': message
            }
        )
        await self.send(text_data=json.dumps({
            'message': message
        }))

        
    # Receive message from room group
    async def control_message(self, event):
        message = event['message']
        print("entro")
        # Send message to WebSocket
        
        await self.send(text_data=json.dumps({
            'message': message
        }))
    




async def llamadaPrueba():

    #cardador = Charger(name="Prueba")

    #cargador = cargadoresOnline[0]
    channel_layer = get_channel_layer()

    for cargador in cargadoresOnline:
        await channel_layer.group_send(
            cargador["controller"],
            {"type": "control_message", "message": "s"},

        )
    #await cargador.imprimir()


    

