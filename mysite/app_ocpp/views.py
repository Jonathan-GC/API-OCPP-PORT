from django.shortcuts import render
from.consumers import Charger, llamadaPrueba
from django.http import HttpResponse

# Create your views here.
def index(request):
    llamadaPrueba()
    return render(request, 'chat/index.html')

def room(request, room_name):
    return render(request, 'chat/room.html', {'room_name': room_name})

async def pedir(request):
    print("estoy en views pidiendo")
    await llamadaPrueba()
    return HttpResponse("Estoy pidiendo que suministre carga")