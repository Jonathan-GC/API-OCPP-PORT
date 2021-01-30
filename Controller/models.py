from django.contrib.auth.models import User
from django.db import models
import uuid


# Model Charger
class Charger_Client(models.Model):
    
    name = models.CharField(max_length=20, blank=True)
    channel_name = models.CharField(max_length=50, blank=True)
    ip_adress = models.GenericIPAddressField(null=True)
    version_ocpp = models.CharField(max_length=5, blank=True)
    available = models.BooleanField(default=False)
    maintenance = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.name}\t{self.ip_adress}"
    
    
    class Meta:
        ordering = ['name']

# Model Transaction
class Transaction(models.Model):
    id_transaction = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE,  null=True)
    charger = models.ForeignKey(Charger_Client, on_delete=models.CASCADE, null=True,)
    datetime = models.DateTimeField(auto_now=True, auto_now_add=False)
    action_name = models.CharField(max_length=50)
    propierties = models.JSONField(null=True)
    error = models.JSONField(null=True)
    type_transaction = models.BooleanField(default=True, null=False, verbose_name="0. Saliente   1. Entrante") 
 
    def __str__(self):
        return f"{self.action_name}\t{self.charger}"
    




'''   
class PropertiesAction(models.Model):
    action_name = models.CharField(max_length=50)
    description = models.JSONField()


class Error(models.Model):
    error_name = models.CharField(max_length=50)
    description = models.JSONField()
'''