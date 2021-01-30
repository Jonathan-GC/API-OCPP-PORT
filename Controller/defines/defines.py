from enum import Enum

class TypeTransaction(str, Enum):
    transactionIn = "transaction in"
    transactionOut = "transaction out"

class Call_Control(str, Enum):
    prefix_control = "charger_controller_"
    start_charging = "s"
    stop_charging = "t"
    