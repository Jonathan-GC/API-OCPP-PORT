
from asgiref.sync import sync_to_async
#importar from data models
from .models import Transaction, Charger_Client
from django.contrib.auth.models import User
from django.contrib import auth
from django.http import HttpResponse


def add_transaction_bd(accion = None, errors=None, **kwargs):
    
    transaction = Transaction(
        action_name=accion,
        propierties=kwargs,
        error=errors
        )

    transaction.save()

    
def isUser(email):

    '''
    Perimite identificar el usuario que inicia la sesion
    aun esta en CONTRUCCION
    '''
    user = User.objects.get(email=email)
    print(user)
    user.get_username()


    if user:
        return True
    else:
        #Return exeption to charger
        #User no Exist
        raise NoUserAuthorize (f"email: {email} no existe")
        


def isChargerAuth(nameCharger):
    '''
    Permite saber si el cargador fue escrito por un administrador
    y le permite realizar la utorizacion y la bootNotification
    '''
    try:
        charger = Charger_Client.objects.get(name = nameCharger)
        name = charger.name
        mantenimiento = charger.maintenance
        disponible = charger.available

        
        if name and not mantenimiento and disponible:
            return True
    except:
        return f"Charger {nameCharger} not available or no exist"

def getChargerName(id):
    try:
        charger = Charger_Client.objects.get(id = id)
        name = charger.name
        return name
    except:
        pass

    #charger = Charger_Client.objects.get(name = nameCharger).only('id', 'name', 'available', 'maintenance' )
    #charger = Charger_Client.objects.filter(name = nameCharger)
    #charger =  Charger_Client.objects.all()
    
    #charger = Charger_Client.objects.get(pk = 3)
    #charger.name = 'joderTio669ttt99'
    #charger.save()

                

    '''
    for ch in charger:
        print(ch)
    '''
    #charger.name = "Joder"
    #charger.save()
    '''
    for ch in charger:
        print(ch)
    '''
    
    '''
    if charger:
        return True
    else:
        return False
        raise NoUserAuthorize (f"Charger: {nameCharger} no existe")
    '''    




