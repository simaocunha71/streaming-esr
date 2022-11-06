import socket
from threading import Thread
import sys
import os
import pickle
from routing import *

listening_port = 0

def processing():
    print("Recebi msg xdxdxd ")

def activeNode_handler(bytesAddressPair):
    ip = bytesAddressPair[1][0]
    msg = bytesAddressPair[0]

    # Ir buscar os vizinhos do nodo que se está a ativar
    neighbours = rt.get_neighbours(ip)
    # Ativar o nodo passando a porta que este está a atender
    rt.active_node(ip,int(msg))

    # Serialize to send
    bytesToSend = pickle.dumps(neighbours)

    UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    UDPClientSocket.sendto(bytesToSend,(ip,int(msg)))

# Server listening
def service_node():
   bufferSize = 1024

   UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

   UDPServerSocket.bind(('',0))

   port = UDPServerSocket.getsockname()[1]

   # O nodo tem que mandar uma menssagem de registo
   msg = str(port)

   bytesToSend = str.encode(msg)
   UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
   UDPClientSocket.sendto(bytesToSend, bootstrapperAddressPort)

   while(True):
       bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)



       thread = Thread(target=processing)
       thread.start()

       message = bytesAddressPair[0]

       data = pickle.loads(message)


       address = bytesAddressPair[1]

       clientMsg = "Message from Client:{}".format(str(data))
       clientIP  = "Client IP Address:{}".format(address)

       print(clientMsg)
       print(clientIP)
   os._exit(0)

# Bootstrapper listening
def service_bootstrapper():
   bufferSize = 1024

   UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

   UDPServerSocket.bind((UDPServerSocket.getsockname()[0],5555))
   print(UDPServerSocket.getsockname()[0])

   while(True):
       bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)

       thread = Thread(target=activeNode_handler,args=[bytesAddressPair])
       thread.start()

       message = bytesAddressPair[0]

       address = bytesAddressPair[1]

       clientMsg = "Message from Client:{}".format(message)
       clientIP  = "Client IP Address:{}".format(address)

       print(clientMsg)
       print(clientIP)
   os._exit(0)

if __name__ == "__main__":

    args = sys.argv[1:]
    n_args = len(args)
    client = False
    bootstrapper = False
    if n_args==1:
        # Adicionar novo nodo à overlay:
        # oNode <bootstrapper_adress>
        bootstrapperAddressPort = (args[0],5555)
        client = True
    elif n_args==2:
        # Iniciar bootstrapper:
        # oNode -bs <config_file>
        if args[0]=="-bs":
            rt = RoutingTable()
            rt.load(args[1])
            #rt.display()
            bootstrapper = True
        elif args[0]=="-c":
            # Executar como cliente:
            # oNode -c <bootstrapper_adress>
            print("Client running")
        else:
             print("ERROR")

    else: print("ERROR")

    # Listening
    if(bootstrapper):

        thread = Thread(target=service_bootstrapper)
        thread.start()
    else:
        thread = Thread(target=service_node)
        thread.start()
