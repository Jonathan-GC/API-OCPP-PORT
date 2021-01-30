from asgiref.sync import async_to_sync
from django.shortcuts import render
from.consumers import Charger, trigger_event
#from django.http import HttpResponse

#importaciones de la api_rest
from .models import Charger_Client, Transaction
from .serializers import Charger_Client_Serializer, Transaction_serializer

from rest_framework import viewsets
from rest_framework.views import APIView
from django.http import Http404

#Importaciones de usuario
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User

class GLOBAL_VARS:
    def __init__(self, userName):
        self.userName = userName


@async_to_sync
async def requerir(id_user, charger, action):
    print("estoy en views pidiendo") 
    await trigger_event(id_user, charger, action)
    

class Charger_ClientViewSet(viewsets.ModelViewSet):
    queryset = Charger_Client.objects.all()
    serializer_class = Charger_Client_Serializer


class Transaction_ViewSet(APIView):
    #authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request, format=None):
        print(request.user)
        
        transactions = Transaction.objects.all()
        serializer  = Transaction_serializer(transactions, many=True)

        return Response(serializer.data)

    
    def post(self, request, format=None):
        
        serializer = Transaction_serializer(data=request.data)

        print(serializer.initial_data)
        if serializer.is_valid():
            #Realizar la operacion de control
            #1. Alamacenar User ID si es valido
            data = serializer.initial_data.values()
            id_user, charger, action = data
            serializer.save()

            #2. Pasar la transaccion al controlador
            requerir(id_user, charger, action)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        

        return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)




# Create your views here.
def index(request):
    trigger_event()
    return render(request, 'chat/index.html')

def room(request, room_name):
    return render(request, 'chat/room.html', {'room_name': room_name})



