import asyncio
import inspect
import logging
import uuid
import re
import time
from dataclasses import asdict

from ocpp.routing import create_route_map
from ocpp.messages import Call, validate_payload, MessageType
from ocpp.exceptions import OCPPError, NotImplementedError
from ocpp.messages import unpack
from channels.generic.websocket import AsyncWebsocketConsumer

from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Process, Queue, Lock

LOGGER = logging.getLogger('ocpp')




def camel_to_snake_case(data):
    """
    Convert all keys of all dictionaries inside the given argument from
    camelCase to snake_case.

    Inspired by: https://stackoverflow.com/a/1176023/1073222

    """
    if isinstance(data, dict):
        snake_case_dict = {}
        for key, value in data.items():
            s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', key)
            key = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

            snake_case_dict[key] = camel_to_snake_case(value)

        return snake_case_dict

    if isinstance(data, list):
        snake_case_list = []
        for value in data:
            snake_case_list.append(camel_to_snake_case(value))

        return snake_case_list

    return data


def snake_to_camel_case(data):
    """
    Convert all keys of a all dictionaries inside given argument from
    snake_case to camelCase.

    Inspired by: https://stackoverflow.com/a/19053800/1073222
    """
    if isinstance(data, dict):
        camel_case_dict = {}
        for key, value in data.items():
            components = key.split('_')
            key = components[0] + ''.join(x.title() for x in components[1:])
            camel_case_dict[key] = snake_to_camel_case(value)

        return camel_case_dict

    if isinstance(data, list):
        camel_case_list = []
        for value in data:
            camel_case_list.append(snake_to_camel_case(value))

        return camel_case_list

    return data


def remove_nones(dict_to_scan):
    dict_to_scan = {
        k: v for k, v in dict_to_scan.items()
        if v is not None
    }
    return dict_to_scan


class ChargePoint(AsyncWebsocketConsumer):
    
    """
    Base Element containing all the necessary OCPP1.6J messages for messages
    initiated and received by the Central System
    """

    async def connect(self, id):
        self.id = id

        try:        
            await self.accept()
            LOGGER.info(f"Charger {self.id} Connected")
            return "201"
        except:
            LOGGER.info(f"Charger {self.id} No Connected")
            return "401"
    
    async def disconnect(cls, close_code):
        pass

    def __init__(self, id = "", response_timeout=5):
        """


        Args:

            charger_id (str): ID of the charger.
            connection: Connection to CP.
            response_timeout (int): When no response on a request is received
                within this interval, a asyncio.TimeoutError is raised.

        """
        super().__init__()
        self.id = id

        # The maximum time in seconds it may take for a CP to respond to a
        # CALL. An asyncio.TimeoutError will be raised if this limit has been
        # exceeded.
        self._response_timeout = response_timeout

        # A connection to the client. Currently this is an instance of gh
        #**self._connection = connection

        # A dictionary that hooks for Actions. So if the CS receives a it will
        # look up the Action into this map and execute the corresponding hooks
        # if exists.
        self.route_map = create_route_map(self)

        #**self._call_lock = asyncio.Lock()
        self.call_lock = False
        self._queue_lock = False

        # A queue used to pass CallResults and CallErrors from
        # the self.serve() task to the self.call() task.
        #**self._response_queue = asyncio.Queue()

        self._response_queue = Queue()
        self._call_queue = Queue()
        
        # Function used to generate unique ids for CALLs. By default
        # uuid.uuid4() is used, but it can be changed. This is meant primarily
        # for testing purposes to have predictable unique ids.
        self.unique_id_generator = uuid.uuid4

    async def start(self, message):

        #Esperando una respuesta
        #print("Paso1: Recibir mensaje")
        LOGGER.info('%s: receive message %s', self.id, message)
        await self.route_message(message)
        
        
        
        

    async def route_message(self, raw_msg):
        """
        Route a message received from a CP.

        If the message is a of type Call the corresponding hooks are executed.
        If the message is of type CallResult or CallError the message is passed
        to the call() function via the response_queue.
        """
        try:
            #print("Paso2: desenpaquetar mensaje en json")
            msg = unpack(raw_msg)
           
        except OCPPError as e:
            LOGGER.exception("Unable to parse message: '%s', it doesn't seem "
                             "to be valid OCPP: %s", raw_msg, e)
            return

        
        if msg.message_type_id == MessageType.Call:

            #print("Paso3: esperando el handleCall")
            await self._handle_call(msg)

        
        elif msg.message_type_id in \
                [MessageType.CallResult, MessageType.CallError]:
            self._response_queue.put_nowait(msg)
            await self.locker()
            
        

    async def _handle_call(self, msg):
        """
        Execute all hooks installed for based on the Action of the message.

        First the '_on_action' hook is executed and its response is returned to
        the client. If there is no '_on_action' hook for Action in the message
        a CallError with a NotImplemtendError is returned.

        Next the '_after_action' hook is executed.

        """
        
        try:
            handlers = self.route_map[msg.action]
            #print("Paso 4: hizo el handle call")
            #print(handlers)
        except KeyError:
            raise NotImplementedError(f"No handler for '{msg.action}' "
                                      "registered.")

        
        if not handlers.get('_skip_schema_validation', False):

            #print("Paso 5: Si no hay esquema de validacion la version ocpp es: ")
            #print(self._ocpp_version)
            validate_payload(msg, self._ocpp_version)

            #print("Paso 6: Despues de la validacion del payload")

        # OCPP uses camelCase for the keys in the payload. It's more pythonic
        # to use snake_case for keyword arguments. Therefore the keys must be
        # 'translated'. Some examples:
        #
        # * chargePointVendor becomes charge_point_vendor
        # * firmwareVersion becomes firmwareVersion
        snake_case_payload = camel_to_snake_case(msg.payload)
        #print("Paso 7: Despues del snakecase")
        #print(snake_case_payload)

        try:
            handler = handlers['_on_action']
            #print("Paso 8: Despues de sacar la accion del handler")
            #print(handler)
            #print(type(handler))

        except KeyError:
            raise NotImplementedError(f"No handler for '{msg.action}' "
                                      "registered.")


        try:
            response = handler(**snake_case_payload)
            #print("Paso 9: Despues de sacar la respuesta")
            #print(response)
            
            if inspect.isawaitable(response):
                response = await response
                #print("Paso 10: Despues de saber si es instanciable")
        except Exception as e:
            LOGGER.exception("Error while handling request '%s'", msg)
            response = msg.create_call_error(e).to_json()
            await self._send(response)

            return

        temp_response_payload = asdict(response)
        #print("Paso 11: Despues de diccionario  temporal")
        #print(temp_response_payload)
        
        # Remove nones ensures that we strip out optional arguments
        # which were not set and have a default value of None
        response_payload = remove_nones(temp_response_payload)
        
        #print("Paso 12: Despues de diccionario ")
        #print(response_payload)
        
        # The response payload must be 'translated' from snake_case to
        # camelCase. So:
        #
        # * charge_point_vendor becomes chargePointVendor
        # * firmware_version becomes firmwareVersion
        camel_case_payload = snake_to_camel_case(response_payload)
        
        #print("Paso 13: convertir respuesta a camel case ")
        #print(camel_case_payload)


        response = msg.create_call_result(camel_case_payload)
        #print("Paso 14: convertir diccionario a respuesta handler ")
        #print(response)

        if not handlers.get('_skip_schema_validation', False):
            validate_payload(response, self._ocpp_version)

        await self._send(response.to_json())

        try:
            handler = handlers['_after_action']
            # Create task to avoid blocking when making a call inside the
            # after handler
            response = handler(**snake_case_payload)
            if inspect.isawaitable(response):
                asyncio.ensure_future(response)
        except KeyError:
            # '_on_after' hooks are not required. Therefore ignore exception
            # when no '_on_after' hook is installed.
            pass
        

    async def call(self, payload, suppress=True):
        """
        Send Call message to client and return payload of response.

        The given payload is transformed into a Call object by looking at the
        type of the payload. A payload of type BootNotificationPayload will
        turn in a Call with Action BootNotification, a HeartbeatPayload will
        result in a Call with Action Heartbeat etc.

        A timeout is raised when no response has arrived before expiring of
        the configured timeout.

        When waiting for a response no other Call message can be send. So this
        function will wait before response arrives or response timeout has
        expired. This is in line the OCPP specification

        Suppress is used to maintain backwards compatibility. When set to True,
        if response is a CallError, then this call will be suppressed. When
        set to False, an exception will be raised for users to handle this
        CallError.

        """

        
        
        camel_case_payload = snake_to_camel_case(asdict(payload))


        call = Call(
            unique_id=str(self.unique_id_generator()),
            #unique_id="tag1234",
            action=payload.__class__.__name__[:-7],
            payload=remove_nones(camel_case_payload)
        )

        validate_payload(call, self._ocpp_version)


        await self._send(call.to_json())
        
        #put call in queue and analizer
        self._call_queue.put(call)
        
        
        # Use a lock to prevent make sure that only 1 message can be send at a
        # a time.
        response = await self.locker(call.unique_id)
        

        if response:
            if response.message_type_id == MessageType.CallError:
                LOGGER.warning("Received a CALLError: %s'", response)
                if suppress:
                    return
                raise response.to_exception()
            else:
                response.action = call.action
                #print("Paso5: reaspuesta action: ", response.action)
                validate_payload(response, self._ocpp_version)

            
            snake_case_payload = camel_to_snake_case(response.payload)
            # Create the correct Payload instance based on the received payload. If
            # this method is called with a call.BootNotificationPayload, then it
            # will create a call_result.BootNotificationPayload. If this method is
            # called with a call.HeartbeatPayload, then it will create a
            # call_result.HeartbeatPayload etc.
            cls = getattr(self._call_result, payload.__class__.__name__)  # noqa
            return cls(**snake_case_payload)
            
        

                    
    async def locker(self, unique_id=None):
        """
        this part allow that each call cans attend it responses
        """ 

        #print(f"Call Size: {self._call_queue.qsize()}\t Responsize: {self._response_queue.qsize()}")
        
        if self._response_queue.qsize():
            if self._call_queue.qsize():
                response = \
                    await self._get_specific_response(
                        self._response_timeout)
            
                #print("Paso4: reaspuesta ", response )
                return response


    async def _get_specific_response(self, timeout):
        """
        Return response with given unique ID or raise an asyncio.TimeoutError.
        """

        
        wait_until = time.time() + timeout

        #[2, "12345", "BootNotification", {"chargePointVendor": "The Mobility House", "chargePointModel": "Optimus"}]
        #[3,"tag1234",{"idTagInfo":{"status":"Accepted"}}]

        try:
            self._process = Process(args=(self._response_queue, self._call_queue))
            self._process.start()
            call = self._call_queue.get_nowait()
            response = self._response_queue.get()
            self._process.join()
        except:
            raise
        
        print(f"Call Size: {self._call_queue.qsize()}\t Responsize: {self._response_queue.qsize()}")
        
        if response.unique_id == call.unique_id:
            return response
    
        
        LOGGER.error('Ignoring response with unknown unique id: %s', response)
        
        '''
        timeout_left = wait_until - time.time()
        
        if timeout_left < 0:
            raise asyncio.TimeoutError

        return await self._get_specific_response(unique_id, timeout_left)
        '''

    async def _send(self, message):
        
        LOGGER.info('%s: send %s', self.id, message)
        await self.send(message)

    async def enviar(self, message):
        
        #LOGGER.info('%s: send %s', self.id, message)
        await self.send(text_data = message)


