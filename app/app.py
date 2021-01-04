from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from central_ocpp.central import *

app = Flask("__main__")

#Definicion de la base de datos
from config.keys import bd_key

bd_name = 'taskPosgres'
bd_route = 'postgresql://' + bd_key + ':admin@localhost:5433/' + bd_name

app.config['SQLALCHEMY_DATABASE_URI'] = bd_route
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#pasar la aplicacion al ORM
db = SQLAlchemy(app)
ma = Marshmallow(app)


db.init_app(app)


@app.route("/")
def home():
    return "Activando el webSocket"


    

if __name__ == '__main__':
    app.run(debug=True)
