import socket
from threading import Thread
import sys
import os
import pickle
from datetime import datetime
from OlyPacket import *
from data import *

listening_port = 0
bufferSize_rtp = 256
bufferSize_oly = bufferSize_bs = 1024
RTP_PORT = 9999
OLY_PORT = 5555

class oNode:
    def __init__(self, isBootstrapper, bootstrapperAddressPort):
        self.isBootstrapper = isBootstrapper
        self.bootstrapperAddressPort = bootstrapperAddressPort
        self.neighbours = []
        self.routingTable = RoutingTable()
        self.streamsTable = StreamsTable()
        if(self.isBootstrapper == True):
            self.olytable = OverlayTable()

    def activeNode_handler(self, bytesAddressPair):
        #print("DISPLAY2")
        #olytable.display()
        ip = bytesAddressPair[1][0]
        msg = bytesAddressPair[0]


        hello_packet = OlyPacket()
        hello_packet = hello_packet.decode(msg)

        if hello_packet.flag=="H":
            print("Recebi mensagem hello | IP: " + ip)
            # Ir buscar os vizinhos do nodo que se ligou
            neighbours = self.olytable.get_neighbours(ip)

            hello_response_packet = OlyPacket()

            hello_response_packet = hello_response_packet.encode("HR",neighbours)


            self.olyClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
            self.olyClientSocket.sendto(hello_response_packet,(ip,OLY_PORT))



    def Oly_handler(self, bytesAddressPair):
        source_ip = bytesAddressPair[1][0]
        msg = bytesAddressPair[0]

        olypacket = OlyPacket()
        olypacket = olypacket.decode(msg)

        print("IP de origem " + source_ip)
        print("OLYPacket FLAG: " + olypacket.flag)

        # Pacote Hello Response
        if olypacket.flag=="HR":
            # O payload é os vizinhos do nodo
            print("Vizinhos")
            print(olypacket.payload)
            self.neighbours = olypacket.payload

        # Pacote de proba
        elif olypacket.flag=="P":
            print("Recebi pacote de prova | IP: " + source_ip)
            now = datetime.now()

            # Timestamp marcado no servidor
            timestamp = olypacket.payload[0]

            delta = now - timestamp

            # Número de saltos do servidor até o nodo atual
            saltos = olypacket.payload[1] + 1

            #cada entrada da tabela assume que é o tempo e custo até ao servidor
            #info ta tabela: source_ip saltos time_cost destinos
            self.routingTable.add_route(source_ip,saltos,delta)
            print("Recebi \"P\"")
            self.routingTable.print()

            # Data a enviar aos nodos viznhos
            data = [timestamp,saltos]

            prob_packet = OlyPacket()
            encoded_prob_packet = prob_packet.encode("P",data)

            # SEMI-TODO identificar se está ligado a um cliente, caso esteja tem que mandar ao servidor a infromação do tempo e nr de saltos

            # O nodo envia mensagem de proba a todos os seus vizinhos ativos
            print("Envio probe para os vizinhos")
            for elem in self.neighbours:
                print(elem['node_ip'])
                if elem['node_ip'] != source_ip:
                    self.olyClientSocket.sendto(encoded_prob_packet,(elem['node_ip'],OLY_PORT))
        else:
            print("Recebi \"else\"")
            self.routingTable.print()
            destination_ip = self.routingTable.next_jump()
            print("FLAG:")
            print(olypacket.flag)
            if olypacket.flag=="SETUP":
                print("Criei novo fluxo |source: " + source_ip  + "| destination: " + destination_ip)

                # Preciso implementar mensagens de proba para conseguirmos saber isto
                # Adicionar um fluxo à routing table falta passar o source (novo vizinho que pediu stream) e dest (novo vizinho a qual o novo atual passa stream)
                self.streamsTable.add_stream(source_ip,destination_ip)

            elif olypacket.flag == "PLAY":
                print("Fluxo ativo | source: "+ source_ip)
                self.streamsTable.open_stream(source_ip)

            elif olypacket.flag == "PAUSE":
                print("Fluxo pausado | source: "+ source_ip)
                # Fecha o fluxo pois o nodo vizinhos(source_ip) não quer stream
                self.streamsTable.close_stream(source_ip)

            elif requestType == "TEARDOWN":
                print("Fluxo fechado | source: "+ source_ip)
                # Passar pacote ao próximo nodo

                # Remover fluxo da tabela de rotas
                self.streamsTable.delete_stream(source_ip)

            self.olyClientSocket.sendto(msg,(destination_ip,RTP_PORT))

    def Rtp_handler(self, address,data):
        # RTP redirect
        # Pacote de stream

        # Ip de onde veio o pedido
        source_ip = address[0]

        destination_ip = self.routingTable.next_jump()

        print("Próximo salto: " + destination_ip)


        self.rtpClientSocket.sendto(data,(destination_ip,RTP_PORT))

    # Listening for OlyPacket
    def service_Oly(self):
        self.olyServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

        self.olyServerSocket.bind(('',OLY_PORT))

        # O nodo tem que mandar uma menssagem de registo
        hello_packet = OlyPacket()
        encoded_packet = hello_packet.encode("H","")

        self.olyClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.olyClientSocket.sendto(encoded_packet, self.bootstrapperAddressPort)

        while(True):
            bytesAddressPair = self.olyServerSocket.recvfrom(bufferSize_oly)

            # Aqui chamamos um handler para interpretar a msg e agir de acordo
            thread = Thread(target=self.Oly_handler,args=[bytesAddressPair])
            thread.start()

        os._exit(0)


    def service_Rtp(self):
       self.rtpServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    
       # A porta para escutar pacotes rtp é fixa
       self.rtpServerSocket.bind(('',RTP_PORT))
       self.rtpClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

       while(True):
           bytesAddressPair = self.rtpServerSocket.recvfrom(bufferSize_rtp)
           data = bytesAddressPair[0]
           address = bytesAddressPair[1]

           thread = Thread(target=self.Rtp_handler,args=(address,data))
           thread.start()




       os._exit(0)

    # Bootstrapper listening
    def service_bootstrapper(self):
       self.olyServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
       self.olyServerSocket.bind(('',OLY_PORT))

       while(True):
           bytesAddressPair = self.olyServerSocket.recvfrom(bufferSize_bs)

            # Aqui chamamos um handler para interpretar a msg e agir de acordo
           thread = Thread(target=self.activeNode_handler,args=[bytesAddressPair])
           thread.start()

       os._exit(0)

if __name__ == "__main__":

    args = sys.argv[1:]
    n_args = len(args)


    if n_args==1:
        print("------------NODE------------")
        # Adicionar novo nodo à overlay:
        # oNode <bootstrapper_adress>

        # Informação de estado do Nodo
        bootstrapperAddressPort = (args[0],OLY_PORT)
        onode = oNode(isBootstrapper=False, bootstrapperAddressPort=bootstrapperAddressPort)

        #UDPClientSocket,routingTable,streamsTable
        thread_RTP = Thread(target=onode.service_Rtp)
        thread_OYP = Thread(target=onode.service_Oly)
        thread_RTP.start()
        thread_OYP.start()
    elif n_args==2:
        # Iniciar bootstrapper:
        # oNode -bs <config_file>
        if args[0]=="-bs":
            print("------------Bootstrapper------------")
            bootstrapper = oNode(isBootstrapper=True, bootstrapperAddressPort="")
            bootstrapper.olytable.load(args[1])
            #rt.display()
            thread = Thread(target=bootstrapper.service_bootstrapper)
            thread.start()
        else:
             print("ERROR")

    else: print("ERROR")
