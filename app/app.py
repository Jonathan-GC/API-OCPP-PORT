from flask import Flask
from flask_sockets import Sockets
import json
import logging

app = Flask(__name__)
sockets = Sockets(app)

HTTP_SERVER_PORT = 5000

@app.route("/")
def index():
    return "Holamundo"

@sockets.route('/media')
def echo(ws):

    while not ws.closed:
        message = ws.receive()
        
        if message is None:
            app.logger.info("No message received")
            continue
    

        # Messages are a JSON encoded string
        data = json.loads(message)
        print(data)
        ws.send(message)


if __name__ == "__main__":
    #app.logger.setLevel(logging.DEBUG)
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler

    server = pywsgi.WSGIServer(('', HTTP_SERVER_PORT), app, handler_class=WebSocketHandler)
    print("Server escuchando en http://localhost:" + str(HTTP_SERVER_PORT))
    server.serve_forever()