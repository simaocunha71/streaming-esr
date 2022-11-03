import socket
from threading import Thread
import sys
import os
from routing import *

def processing():
    print("Recebi msg")

def processing_active_onode(bytesAddressPair):
    ip = bytesAddressPair[1][0]
    msg = bytesAddressPair[0]
    print(ip)
    neighbours = rt.get_neighbours(ip)
    bytesToSend = str.encode(str(neighbours))
    UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    UDPClientSocket.sendto(bytesToSend, (ip,int(msg)))
# Server listening
def service():
   bufferSize = 1024

   UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

   UDPServerSocket.bind(('',0))

   port = UDPServerSocket.getsockname()[1]
   
   msg = str(port)
   bytesToSend = str.encode(msg)
   UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
   UDPClientSocket.sendto(bytesToSend, bootstrapperAddressPort)

   while(True):
       bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)

       thread = Thread(target=processing)
       thread.start()

       message = bytesAddressPair[0]

       address = bytesAddressPair[1]

       clientMsg = "Message from Client:{}".format(message)
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

       thread = Thread(target=processing_active_onode,args=[bytesAddressPair])
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
        # eNode <bootstrapper_ip>
        bootstrapperAddressPort = (args[0],5555)
        client = True
    elif n_args==2:
        # Iniciar bootstrapper:
        # eNode -bs <config_file>
        if args[0]=="-bs":
            rt = RoutingTable()
            rt.load(args[1])
            #rt.display()
            bootstrapper = True
        else: print("ERROR")

    else: print("ERROR")
    
    

    # Listening
    if(bootstrapper):
        thread = Thread(target=service_bootstrapper)
        thread.start()
    else: 
        thread = Thread(target=service)
        thread.start()


