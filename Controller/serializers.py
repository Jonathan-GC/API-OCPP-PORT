from .models import Charger_Client, Transaction
from rest_framework import serializers

class Charger_Client_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Charger_Client
        fields = ['name', 'ip_adress', 'version_ocpp', 'available']

class Transaction_serializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['user', 'charger', 'action_name', 'id_transaction']
'''
class UserCharger_TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserChargerTransaction
        #fields = ['id_transaction', 'user', 'datetime', 'transaction']
        fields = "__all__"
'''