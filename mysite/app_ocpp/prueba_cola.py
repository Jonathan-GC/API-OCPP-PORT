from multiprocessing import Process, Queue, Lock
import time

cola = Queue()



if __name__ == "__main__":

    while True:

        msgIn = input("Cual es el mensaje: ")

        if "$" in msgIn:
            print("si es un dolar")
            cola.put_nowait(msgIn) 
            
        if "#" in msgIn:
            print ("tamaño conla ", cola.qsize())
            break

    
    
    #<class 'ocpp.messages.CallResult'>
    #<class 'ocpp.messages.Call'>
    
    for n in range( cola.qsize()):
        proceso = Process(args=(cola,))
        proceso.start()
        print(cola.get( timeout=2))
    
        proceso.join()
    