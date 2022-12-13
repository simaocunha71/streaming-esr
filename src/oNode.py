import socket
from threading import Thread
import sys
import os
import pickle
import random
from datetime import datetime
from OlyPacket import *
from data import *
from RtpPacket import RtpPacket

RTP_BUFFER_SIZE = 20480
OLY_BUFFER_SIZE = 250

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

        if hello_packet.type=="H":
            print("Recebi mensagem hello | IP: " + ip)
            # Ir buscar os vizinhos do nodo que se ligou
            neighbours = self.olytable.get_neighbours(ip)
            data = neighbours
            data.append(ip)

            hello_response_packet = OlyPacket()

            hello_response_packet = hello_response_packet.encode("HR",data)


            self.olyClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
            self.olyClientSocket.sendto(hello_response_packet,(ip,OLY_PORT))



    def Oly_handler(self, bytesAddressPair):
        source_ip = bytesAddressPair[1][0]
        msg = bytesAddressPair[0]

        olypacket = OlyPacket()
        olypacket = olypacket.decode(msg)

        print("IP de origem " + source_ip)
        print("OLYPacket FLAG: " + olypacket.type)

        # Pacote Hello Response
        if olypacket.type=="HR":
            # O payload é os vizinhos do nodo
            print("Vizinhos")
            print(olypacket.payload)

            data = olypacket.payload
            self.neighbours = data[:-1]
            self.ip = data[-1]

        # Pacote de proba
    elif olypacket.type=="P":
            print("Recebi pacote de prova | IP: " + source_ip)
            now = datetime.now()

            # Timestamp marcado no servidor
            timestamp = olypacket.payload[0]

            delta = now - timestamp

            # Número de saltos do servidor até o nodo atual
            saltos = olypacket.payload[1] + 1

            # IP de quem enviou pacote de probe
            probe_source_ip = olypacket.payload[2]

            #cada entrada da tabela assume que é o tempo e custo até ao servidor
            #info ta tabela: source_ip saltos time_cost destinos
            self.routingTable.add_route(source_ip,saltos,delta)
            print("Recebi \"P\"")
            self.routingTable.print()

            # Data a enviar aos nodos viznhos
            data = [timestamp,saltos,self.ip]

            prob_packet = OlyPacket()
            encoded_prob_packet = prob_packet.encode("P",data)

            # O nodo envia mensagem de proba a todos os seus vizinhos ativos
            print("Envio probe para os vizinhos")
            for elem in self.neighbours:
                print("NodeIP: " + elem + " | SOURCEIP: " + source_ip)
                if elem != probe_source_ip:
                    self.olyClientSocket.sendto(encoded_prob_packet,(elem,OLY_PORT))
        else:
            self.routingTable.print()
            destination_ip = self.routingTable.next_jump()

            if olypacket.type=="SETUP":
                print("Criei novo fluxo |source: " + source_ip  + "| destination: " + destination_ip)
                # Preciso implementar mensagens de proba para conseguirmos saber isto
                # Adicionar um fluxo à routing table falta passar o source (novo vizinho que pediu stream) e dest (novo vizinho a qual o novo atual passa stream)
                first_stream = self.streamsTable.is_empty()
                self.streamsTable.add_stream(source_ip,destination_ip)

                if(first_stream):
                    self.olyClientSocket.sendto(msg,(destination_ip,OLY_PORT))

            elif olypacket.type == "PLAY":
                print("Fluxo ativo")
                old_status = self.streamsTable.stream_table_status()
                self.streamsTable.open_stream(source_ip)
                new_status = self.streamsTable.stream_table_status()

                if(old_status != new_status):
                    self.olyClientSocket.sendto(msg,(destination_ip,OLY_PORT))

            elif olypacket.type == "PAUSE":
                print("Fluxo pausado")
                # Fecha o fluxo pois o nodo vizinhos(source_ip) não quer stream
                old_status = self.streamsTable.stream_table_status()
                self.streamsTable.close_stream(source_ip)
                new_status = self.streamsTable.stream_table_status()

                if(old_status != new_status):
                    self.olyClientSocket.sendto(msg,(destination_ip,OLY_PORT))

            elif olypacket.type == "TEARDOWN":
                print("Fluxo fechado")
                # Passar pacote ao próximo nodo

                old_status = self.streamsTable.stream_table_status()
                # Remover fluxo da tabela de rotas
                self.streamsTable.delete_stream(source_ip)
                new_status = self.streamsTable.stream_table_status()

                empty = self.streamsTable.is_empty()

                if(empty):
                    self.olyClientSocket.sendto(msg,(destination_ip,OLY_PORT))
                elif(old_status != new_status):
                    msg = olypacket.encode("PAUSE",[])
                    self.olyClientSocket.sendto(msg,(destination_ip,OLY_PORT))


    def Rtp_handler(self, address,data):
        # RTP redirect
        # Pacote de stream

        # Ip de onde veio o pedido
        source_ip = address[0]
        open_streams = self.streamsTable.get_streams()

        #stream.source: endereços sao guardados inicialmente do sv para o cliente. Logo é necessário chamá-los pela ordem inversa
        for stream in open_streams:
            print("Redirecionei pacote de stream " + source_ip + " -> " + stream.source)
            self.rtpClientSocket.sendto(data,(stream.source,RTP_PORT))


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
            bytesAddressPair = self.olyServerSocket.recvfrom(OLY_BUFFER_SIZE)

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
           bytesAddressPair = self.rtpServerSocket.recvfrom(RTP_BUFFER_SIZE)
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
           bytesAddressPair = self.olyServerSocket.recvfrom(OLY_BUFFER_SIZE)

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
