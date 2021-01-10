from flask import Flask, request, jsonify, json
from flask_marshmallow import Marshmallow
from flask_sockets import Sockets


app = Flask(__name__)
sockets = Sockets(app)

HTTP_SERVER_PORT = 5000
mensaje = ""


#pasar la aplicacion al ORM
ma = Marshmallow(app)

#Global variables
consulta = ""


class Task():

    """A Call:
        is a type of message that initiate a request/response sequence.
        Both central systems and charge points can send this message.

    From the specification:

        A Call always consists of 4 elements: The standard elements
        MessageTypeId and UniqueId, a specific Action that is required on the
        other side and a payload, the arguments to the Action. The syntax of a
        call looks like this:

            [<MessageTypeId>, "<UniqueId>", "<Action>", {<Payload>}]

        ...

        For example, a BootNotification request could look like this:

            [2,
             "19223201",
             "BootNotification",
             {
              "chargePointVendor": "VendorX",
              "chargePointModel": "SingleSocketCharger"
             }
            ]
    """
    
    def __init__(self, MessageTypeId, UniqueId, Action, Payload):
        
        self.MessageTypeId = MessageTypeId
        self.UniqueId = UniqueId
        self.Action = Action
        self.Payload = Payload


#Crear un squema
class TaskSchema(ma.Schema):
    class Meta:
        fields = ('MessageTypeId', 'UniqueId', 'Action', 'Payload')

##Para interactuar con el elemento solamente es llamar a task_schema, para actualizar y o eliminar
task_schema = TaskSchema()
##Si quiero obtener multiples datos
tasks_schema = TaskSchema(many=True)


@app.route("/charger/<id>", methods = ["POST"])
def getCharger(id):
    global consulta

    #Imprimir el objeto que viene
    peticion, id_transaction, action, arguments = request.json
    new_task = Task(peticion, id_transaction, action, arguments)
    consulta = peticion, id_transaction, action, arguments
    consulta = json.dumps(consulta, indent=4)
    echo(None, dato=consulta)

    return task_schema.jsonify(new_task)

''''
class ChargePoint(cp):
    
    #Decorador principal de pedido clientes 
    @on(Action.BootNotification)
    def on_boot_notitication(self, charge_point_vendor: str, charge_point_model: str, **kwargs):
        return call_result.BootNotificationPayload(
            current_time=datetime.utcnow().isoformat(),
            interval=10,
            status=RegistrationStatus.accepted
        )
'''


@sockets.route('/media')
def echo(ws, dato=None ):
    '''
    global mensaje
    global consulta
    while not ws.closed:
        message = ws.receive()
        
        if message is None:
            app.logger.info("No message received")
            continue
    

        # Messages are a JSON encoded string
        data = json.loads(message)
        data[0] = 3
        print(data)
        mensaje = ", ".join(str(_) for _ in data)
        print(type(consulta))
        print(consulta)
        ws.send(consulta)
    '''
    while not ws.closed:
        message = ws.receive()
        print(message)
        
        ws.send("consulta")






if __name__ == "__main__":
    #app.logger.setLevel(logging.DEBUG)
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler

    server = pywsgi.WSGIServer(('', HTTP_SERVER_PORT), app, handler_class=WebSocketHandler)
    print("Server escuchando en http://localhost:" + str(HTTP_SERVER_PORT))
    server.serve_forever()