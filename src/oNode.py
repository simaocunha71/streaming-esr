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


def Oly_handler(bytesAddressPair,neighbours,routingTable):
    ip = bytesAddressPair[1][0]
    msg = bytesAddressPair[0]

    olypacket = OlyPacket()
    olypacket = olypacket.decode(msg)

    # Pacote Hello Response
    if olypacket.flag=="HR":
        # O payload é os vizinhos do nodo
        print("Vizinhos")
        print(olypacket.payload)
        neighbours = olypacket.payload

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




def Rtp_handler(address,data):
    # Implementar rtp handler
    """Process RTSP request sent from neighbour node."""
    # Get the request type
    request = data.split('\n')
    line1 = request[0].split(' ')
    requestType = line1[0]

    # Get the media file name
    filename = line1[1]

    # Get the RTSP sequence number
    line2 = request[1].split(' ')
    seq = line2[0]

    # Ip de onde veio o pedido
    source_ip = address[0]

    # Process SETUP request
    if requestType == "SETUP":

        # Preciso implementar mensagens de proba para conseguirmos saber isto
        destination_ip = "Temos que saber o caminho mais rapido para o servidor?????"
        # Adicionar um fluxo à routing table falta passar o source (novo vizinho que pediu stream) e dest (novo vizinho a qual o novo atual passa stream)
        routingTable.add_stream(source_ip,destination_ip)

        # Difundir o pacote para o próximo nodo

    # Process PLAY request
    elif requestType == "PLAY":

        routingTable.open_stream(source_ip)
        # Passar pacote ao próximo nodo
        # Ler a tabela de rotas passar saber a que nodo passar o pacote


    # Process PAUSE request
    elif requestType == "PAUSE":

        # Fecha o fluxo pois o nodo vizinhos(source_ip) não quer stream
        routingTable.close_stream(source_ip)

        # Passar pacote ao próximo nodo
        # Ler a tabela de rotas passar saber a que nodo passar o pacote

    # Process TEARDOWN request
    elif requestType == "TEARDOWN":

        # Passar pacote ao próximo nodo


        # Remover fluxo da tabela de rotas
        routingTable.delete_stream(source_ip)


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
        thread = Thread(target=Oly_handler,args=(bytesAddressPair,routingTable,neighbours))
        thread.start()

    os._exit(0)


def service_Rtp():

   bufferSize = 256

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

       data = bytesAddressPair[0].decode("utf-8")

       address = bytesAddressPair[1]


       thread = Thread(target=Rtp_handler,args=(address,data))
       thread.start()




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

        # Informação de estado do Nodo
        neighbours = []
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
