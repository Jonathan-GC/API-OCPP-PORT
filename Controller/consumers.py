# chat/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async

import uuid
import logging
from datetime import datetime
import asyncio
from ocpp.routing import on, after
from ocpp.v16 import ChargePoint as cp

from ocpp.v16.enums import Action, RegistrationStatus, AuthorizationStatus, RemoteStartStopStatus
from ocpp.v16 import call_result, call

from channels.layers import get_channel_layer
from channels.consumer import SyncConsumer

logging.basicConfig(level=logging.INFO)

from .defines.defines import Call_Control
from .operaciones_bd import *


cargadoresOnline = []

id_token_transaction = uuid.uuid4



class ActionCharger:
    errors=[]
    nombreCargador = ""
    @on(Action.BootNotification)
    def on_boot_notification(self, charge_point_vendor: str, charge_point_model: str, **kwargs):
        
        auth = isChargerAuth(self.nombreCargador)
        status = None
        if auth == True:
            status=RegistrationStatus.accepted
        else:
            status=RegistrationStatus.rejected
            self.errors.append(auth)

        return call_result.BootNotificationPayload(
                current_time=datetime.utcnow().isoformat(),
                interval=10,
                status=status
            )

    
    @after(Action.BootNotification)
    def after_boot_notification(self, **kwargs):
        catch = dict(error = self.errors)
        add_transaction_bd("BootNotification", errors=catch , **kwargs)
        

    try:
        @on(Action.Authorize)
        def on_authorize_response(self, id_tag: str, **kwargs):
            self.idTag = id_tag
            auth = isChargerAuth(self.nombreCargador)
            status = None
            if auth == True:
                status=RegistrationStatus.accepted
            else:
                status=RegistrationStatus.rejected
                self.errors.append(auth)


            return call_result.AuthorizePayload(
                id_tag_info={
                    "status" : AuthorizationStatus.invalid
                }
            )

        @after(Action.Authorize)
        def after_authorize_response(self, **kwargs):
            try:
                add_transaction_bd("authorize", **kwargs)
            except Exception:
                catch = dict(error = Exception)
                add_transaction_bd("authorize", error=catch)
            
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
    @sync_to_async
    def after_status_notification(self, **kwargs):
        try:
            add_transaction_bd("StatusNotification", **kwargs)
        except Exception:
            catch = dict(error = Exception)
            add_transaction_bd("StatusNotification", error=catch)

    @on(Action.MeterValues)
    def on_meter_values (self, connector_id: int, **kwargs):
        return call_result.MeterValuesPayload(
            
        )

    @after(Action.MeterValues)
    @sync_to_async
    def after_meter_values (self, **kwargs):
        add_transaction_bd("MeterValues", **kwargs)

    
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
        self.room_charger_controller = 'charger_controller_%s' % self.charger_name
        
        # Join room charger controller
        await self.channel_layer.group_add(
            self.room_charger_controller,
            self.channel_name
        )

        ActionCharger.nombreCargador = self.charger_name
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
        await super().start(text_data)
        '''
        #Esto es temporal y es para probar solamente la StopTransaction
        if text_data == Call_Control.start_charging.value:
            await self.start_charge_remote()
        elif text_data == Call_Control.stop_charging.value: 
            await self.stop_charge_remote()
        else:
            await super().start(text_data)
        '''

    # Receive message from room controller
    async def control_message(self, event):
        message = event['message']
        # Send message to WebSocket
        if message == Call_Control.start_charging.value:
            await self.start_charge_remote()
        if message == Call_Control.stop_charging.value:
            await self.stop_charge_remote()





async def trigger_event(user, charger, action):
    charger = getChargerName(charger)

    channel_layer = get_channel_layer()
    channel_room = Call_Control.prefix_control + charger
    msn = None
    if action == "StartRemoteTransaction":
        msn = Call_Control.start_charging.value

    elif action == "StopRemoteTransaction":
        msn = Call_Control.stop_charging.value
    
    await channel_layer.group_send(
            channel_room,
            {"type": "control_message", "message": msn},

        )



    

