import socket
from threading import Thread
import sys
import os
from routing import *


def server():
   # Create a datagram socket
   bufferSize = 1024
   UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
   UDPServerSocket.bind(('',0))
   print(UDPServerSocket.getsockname()[1])
   while(True):
       bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)

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

    if n_args==2:

        # Adicionar novo nodo à overlay:
        # eNode -j <bootstrapper_port>
        if args[0]=="-j" :
            serverAddressPort = ('',int(args[1]))

        # Iniciar bootstrapper:
        # eNode -bs <config_file>
        elif args[0]=="-bs":
            rt = RoutingTable()
            rt.load(args[1])
            rt.display()


    # Listening
    thread = Thread(target=server)
    thread.start()

    # Create a UDP socket at client side
    UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    while True:
        msg = input()
        bytesToSend = str.encode(msg)
        UDPClientSocket.sendto(bytesToSend, serverAddressPort)
