import socket
from threading import Thread
import sys
import os
from routing import *

def processing():
    print("Recebi msg")
# Server listening
def service():
   bufferSize = 1024

   UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

   UDPServerSocket.bind(('',0))

   port = UDPServerSocket.getsockname()[1]
   print(port)
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


if __name__ == "__main__":

    args = sys.argv[1:]
    n_args = len(args)


    # Listening
    thread = Thread(target=service)
    thread.start()

    serverAddressPort = ('',int(args[0]))
    # Create a UDP socket at client side
    UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    while True:
        msg = input()
        bytesToSend = str.encode(msg)
        UDPClientSocket.sendto(bytesToSend, serverAddressPort)
