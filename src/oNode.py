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


def Oly_handler():
    # Implementar handler
    pass


def Rtp_handler():
    # Implementar rtp handler
    pass

# Listening for OlyPacket
def service_Oly():
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

        # Aqui chamamos um handler para interpretar a msg e agir de acordo
        thread = Thread(target=Oly_handler)
        thread.start()

        message = bytesAddressPair[0]

        data = pickle.loads(message)


        address = bytesAddressPair[1]

        clientMsg = "Message from Client:{}".format(str(data))
        clientIP  = "Client IP Address:{}".format(address)

        print(clientMsg)
        print(clientIP)
    os._exit(0)


def service_Rtp():
   bufferSize = 1024

   UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

   # A porta para escutar pacotes rtp é fixa
   UDPServerSocket.bind(('',9999))

   port = UDPServerSocket.getsockname()[1]

   # O nodo tem que mandar uma menssagem de registo
   msg = str(port)

   bytesToSend = str.encode(msg)
   UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
   UDPClientSocket.sendto(bytesToSend, bootstrapperAddressPort)

   while(True):
       bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)

       # Aqui chamamos um handler para interpretar a msg e agir de acordo
       thread = Thread(target=Rtp_handler)
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

        # Aqui chamamos um handler para interpretar a msg e agir de acordo
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

    if n_args==1:
        # Adicionar novo nodo à overlay:
        # oNode <bootstrapper_adress>
        bootstrapperAddressPort = (args[0],5555)
        thread_RTP = Thread(target=service_Rtp)
        thread_OYP = Thread(target=service_Oly)
        thread_RTP.start()
        thread_OYP.start()
    elif n_args==2:
        # Iniciar bootstrapper:
        # oNode -bs <config_file>
        if args[0]=="-bs":
            print("Bootstrapper running..")
            rt = RoutingTable()
            rt.load(args[1])
            #rt.display()
            thread = Thread(target=service_bootstrapper)
            thread.start()
        else:
             print("ERROR")

    else: print("ERROR")
