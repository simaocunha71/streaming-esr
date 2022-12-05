import socket
from threading import Thread
import sys
import os
import pickle
from datetime import datetime
from OlyPacket import *
from data import *

listening_port = 0

def processing():
    print("Recebi msg xdxdxd ")

def activeNode_handler(bytesAddressPair,rt):
    ip = bytesAddressPair[1][0]
    msg = bytesAddressPair[0]

    test_ip = "10.0.2.2"

    hello_packet = OlyPacket()
    hello_packet = hello_packet.decode(msg)

    if hello_packet.flag=="H":
        # Ir buscar os vizinhos do nodo que se está a ativar
        neighbours = rt.get_neighbours(test_ip)
        # Ativar o nodo passando a porta que este está a atender
        rt.active_node(test_ip,hello_packet.payload)

        hello_response_packet = OlyPacket()

        hello_response_packet = hello_response_packet.encode("HR",neighbours)


        UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        UDPClientSocket.sendto(hello_response_packet,(ip,hello_packet.payload))


def Oly_handler(bytesAddressPair,routingTable):
    ip = bytesAddressPair[1][0]
    msg = bytesAddressPair[0]

    olypacket = OlyPacket()
    olypacket = olypacket.decode(msg)

    # Pacote Hello Response
    if olypacket.flag=="HR":
        # O payload é os vizinhos do nodo
        print("Vizinhos")
        print(olypacket.payload)
        # Cria um possivel fluxo por cada nodo vizinha na tabela de routing
        for node in olypacket.payload:
            routingTable.add_stream(node['node_ip'])

    # Pacote de proba
    elif olypacket.flag=="P":

        UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        UDPClientSocket.sendto(hello_response_packet,(ip,hello_packet.payload))

        now = datetime.now()
        timestamp = olypacket.payload[0]
        delta = now - timestamp
        saltos = olypacket.payload[1] + 1

        # Falta adiconar a uma tabela de rotas, para o nodo saber o melhor caminho

        # Timestamp que o servidor marcou na primeira mensagem de proba
        # Saltos até nr de saltos até ao momento
        data = [timestamp,saltos]

        prob_packet = OlyPacket()
        encoded_prob_packet = prob_packet.encode("P",data)

        # FALTA identificar se está ligado a um cliente, caso esteja tem que mandar ao servidor a infromação do tempo e nr de saltos

        # O nodo envia mensagem de proba a todos os seus vizinhos ativos
        for elem in neighbours:
            if elem['port']!=-1:
                UDPClientSocket.sendto(encoded_prob_packet,(elem['ip'],elem['port']))




def Rtp_handler():
    # Implementar rtp handler

    # Lidar com pacotes de stream

    # Lidar com pedidos de stream

    # Lidar com abandonos de stream
    pass

# Listening for OlyPacket
def service_Oly():
    bufferSize = 1024

    UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    UDPServerSocket.bind(('',0))

    port = UDPServerSocket.getsockname()[1]

    # O nodo tem que mandar uma menssagem de registo
    hello_packet = OlyPacket()
    encoded_packet = hello_packet.encode("H",port)

    UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    UDPClientSocket.sendto(encoded_packet, bootstrapperAddressPort)

    while(True):
        bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)

        # Aqui chamamos um handler para interpretar a msg e agir de acordo
        thread = Thread(target=Oly_handler,args=(bytesAddressPair,routingTable))
        thread.start()

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
       thread = Thread(target=activeNode_handler,args=(bytesAddressPair,rt))
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
        routingTable = RoutingTable()
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
            rt = OverlayTable()
            rt.load(args[1])
            #rt.display()
            thread = Thread(target=service_bootstrapper)
            thread.start()
        else:
             print("ERROR")

    else: print("ERROR")
