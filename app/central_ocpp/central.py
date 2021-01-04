import asyncio
import logging
from datetime import datetime
import json
import websockets
import sys


#Importaciones Clave
from ocpp.routing import on, after
from ocpp.v16 import ChargePoint as cp
from ocpp.v16.enums import Action, RegistrationStatus, AuthorizationStatus, RemoteStartStopStatus
from ocpp.v16 import call_result, call

#Nivel de acceso 
logging.basicConfig(level=logging.INFO)
logging.basicConfig()
STATE = {"value": 0}
USERS = set()
hayControlRemoto = 0
EV = None

#Variables de Transaccion
idConector = 0
idTag = "" 

def state_event():
    recibe = json.dumps({"type": "state", **STATE})
    return recibe

def users_event():
    recibe = json.dumps({"type": "users", "count": len(USERS)})
    return recibe

async def notify_state():
    if USERS:  # asyncio.wait doesn't accept an empty list
        message = state_event()
        print(message)
        await asyncio.wait([user.send(message) for user in USERS])


async def notify_users():
    if USERS:  # asyncio.wait doesn't accept an empty list
        message = users_event()
        print(message)
        await asyncio.wait([user.send(message) for user in USERS])


async def register(websocket):
    print(websocket)
    USERS.add(websocket)
    await notify_users()


async def unregister(websocket):
    USERS.remove(websocket)
    await notify_users()


async def counter(websocket, path, objeto_ocpp = None):
    # register(websocket) sends user_event() to websocket

    await register(websocket)
    try:
        await websocket.send(state_event())
        async for message in websocket:
            data = json.loads(message)
            print(data)
            if data["action"] == "Stop":
                STATE["value"] = 0
                await notify_state()
                #objeto_ocpp.on_remote_start_transaction( {"status" : "Accepted"})
                if(objeto_ocpp != None ):
                    await objeto_ocpp.enviarOrden(STATE["value"])
                
                #await cp2.enviar(message)

            elif data["action"] == "Start":
                STATE["value"] = 1
                await notify_state()
                #objeto_ocpp.on_remote_start_transaction({"status" : "Accepted"})
                if(objeto_ocpp != None ):
                    await objeto_ocpp.enviarOrden(STATE["value"])
                
                
            else:
                logging.error("unsupported event: {}", data)
    finally:
        await unregister(websocket)





class ChargePoint(cp):
    
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
        def on_authorize_response(self, id_tag: str, **kwargs):
            global idTag
            idTag = id_tag
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
        global idConector
        idConector = connector_id
        return call_result.StatusNotificationPayload(

        )
    
    @after(Action.StatusNotification)
    def imprimirMenssage(self, connector_id: int, error_code: str, status: str, timestamp: str, info: str, vendor_id: str, vendor_error_code: str, **kwargs):
        print("tomando Pulso del cargador")

    @on(Action.MeterValues)
    
    def on_meter_values (self, connector_id: int, **kwargs):
        return call_result.MeterValuesPayload(
            
        )


    async def notify_stateCP(self):       
        if USERS:  # asyncio.wait doesn't accept an empty list
            message = state_event()
            print("entro en CP: ", message)
            await asyncio.wait([user.send(message) for user in USERS])

    async def enviarOrden(self, run = None):
        global idTag
        global idConector
        if run:
            print("enviando orden de carga remota")
            msn = call.RemoteStartTransactionPayload(
                id_tag = str(idTag),
                connector_id = idConector
                
                    
            )
            response = await self.call(msn)
        else:
            print("Detener orden de carga remota")
            msn= call.RemoteStopTransactionPayload(
                transaction_id = 1
            )
            response = await self.call(msn)


async def on_connect(websocket, path):
    """ For every new charge point that connects, create a ChargePoint instance
    and start listening for messages.

    """
    try:
        global EV
        global hayControlRemoto
        charge_point_id = path.strip('/')

        
        if (charge_point_id != "RemotoControl" ):
            print("Es un cargador")
            cp = ChargePoint(charge_point_id, websocket)
            EV = cp
            print ("EV es cp: ", EV is cp) 
            print (EV) 
            await cp.start()
            
        else:
            print("Es un Control Remoto")
            print (EV) 
            await counter(websocket, path, EV)
        
    except websockets.exceptions.ConnectionClosedOK:
        print ("Cliente Cerrado")
    
        



async def main():
    
    server2 = await websockets.serve(
        on_connect,
        'localhost',
        #'0.0.0.0',
        9000,
        #'149.56.47.168',
        #8080,
        subprotocols=['ocpp1.6']
    )

    await server2.wait_closed()
    

if __name__ == '__main__':
    try:
        # asyncio.run() is used when running this example with Python 3.7 and
        # higher.
        asyncio.run(main())
    except AttributeError:
        # For Python 3.6 a bit more code is required to run the main() task on
        # an event loop.
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
        loop.close()
