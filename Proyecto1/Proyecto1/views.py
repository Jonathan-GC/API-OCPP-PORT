from django.http import HttpResponse
import datetime
import os.path
from django.template import Template, Context
from django.template import loader

def saludo(request, persona):  #primera Vista
    #doc_externo = open("C:/Users/Administrador/Documents/GitHub/API-OCPP-PORT/Proyecto1/Proyecto1/templates/index.html")
    #templa=Template(doc_externo.read())
    ##Cerrar el documento
    #doc_externo.close()

    #usanndo cargadores
    doc_externo = loader.get_template("index.html")

    
    #Crear contexto
    #ctx=Context({"persona":persona, "temas": ["objetos", "mapas", "websokets"]})

    ##Renderizar Contexto
    #documento = templa.render(ctx)
    documento = doc_externo.render({"persona":persona, "temas": ["objetos", "mapas", "websokets"]})

    return HttpResponse(documento)

def despedida(request):  #2nd Vista
    return HttpResponse("chao Tio")

def getFecha(request):

    fechaActual = datetime.datetime.now()
    cadena = " la fecha es: %s " % fechaActual
    return HttpResponse(cadena)

def calc_edad(request, edadActual,  anio):
    
    periodo = anio - 2020
    edad_futura = periodo+edadActual
    cadena = f"en el año {anio} tendrás {edad_futura} años"
    return HttpResponse(cadena)
