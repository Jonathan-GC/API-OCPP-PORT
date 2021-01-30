from django.contrib import admin
from Controller.models import Charger_Client, Transaction

# Register your models here.
admin.site.register(Charger_Client)
admin.site.register(Transaction)