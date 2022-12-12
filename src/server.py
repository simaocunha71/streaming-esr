import sys, socket
from datetime import datetime

from threading import Thread
from OlyPacket import OlyPacket
from ServerWorker import ServerWorker

bufferSize = 1024
rtsp_bufferSize = 256
OLY_PORT = 5555
RTP_PORT = 9999


class Server:

    def oly_handler(self,bytesAddressPair,neighbours, UDPClientSocket):
        ip = bytesAddressPair[1][0]
        msg = bytesAddressPair[0]
        olypacket = OlyPacket()
        olypacket = olypacket.decode(msg)
        if olypacket.flag == "HR":
            # Recebe vizinhos do bootstrapper
            neighbours = olypacket.payload
            print("Vizinhos")
            print(neighbours)


            # O server depois de saber o vizinho inicia o seu worker que dá handle aos pacotes
            # de sessão e trata do envio dos pacotes de stream
            if neighbours:
                rtspSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

                rtspSocket.bind(('',RTP_PORT))

                clientInfo = {}
                clientInfo['rtspSocket'] = rtspSocket
                ServerWorker(clientInfo,neighbours[0],RTP_PORT).run()


            # Cria mensagem de proba
            probe_message = OlyPacket()
            timestamp = datetime.now()
            saltos = 0
            data = [timestamp,saltos]
            probe_message = probe_message.encode("P",data)

            print("Mensagem de proba enviada")
            # Envia mensagem de proba para o vizinho (o servidor só tem um vizinho)
            UDPClientSocket.sendto(probe_message,(neighbours[0]['node_ip'],OLY_PORT))

    def oly_service(self, bs_ip):
        UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        UDPServerSocket.bind(('',0))
        port = UDPServerSocket.getsockname()[1]

        # O nodo tem que mandar uma menssagem de registo

        hello_packet = OlyPacket()
        encoded_packet = hello_packet.encode("H",port)
        UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        UDPClientSocket.sendto(encoded_packet,(bs_ip,OLY_PORT)) #bootstrapper fica a escuta na porta 5555
        # Servidor fica à escuta de OlyPackets
        while(True):
            bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
            neighbours = []
            # Aqui chamamos um handler para interpretar a msg e agir de acordo
            thread = Thread(target=Server.oly_handler,args=(Server,bytesAddressPair,neighbours, UDPClientSocket))
            thread.start()
        os._exit(0)

if __name__ == "__main__":

    UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    UDPServerSocket.bind(('',OLY_PORT))
    bs_ip = sys.argv[1]

    # O nodo tem que mandar uma menssagem de registo

    hello_packet = OlyPacket()
    encoded_packet = hello_packet.encode("H","")
    UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    UDPClientSocket.sendto(encoded_packet,(bs_ip,OLY_PORT))

    bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)

    ip = bytesAddressPair[1][0]
    msg = bytesAddressPair[0]
    olypacket = OlyPacket()
    olypacket = olypacket.decode(msg)
    if olypacket.flag == "HR":
        # Recebe vizinhos do bootstrapper
        data = olypacket.payload
        neighbours = data[:-2]
        server_ip = data[-2]

        print("Vizinhos")
        print(neighbours)

        # Cria mensagem de proba
        probe_message = OlyPacket()
        timestamp = datetime.now()
        saltos = 0
        data = [timestamp,saltos, server_ip]
        probe_message = probe_message.encode("P",data)

        print("Mensagem de proba enviada")
        # Envia mensagem de proba para o vizinho (o servidor só tem um vizinho)
        UDPClientSocket.sendto(probe_message,(neighbours[0]['node_ip'],OLY_PORT))

        # Servidor escuta por novos pedidos cliente
        while True:
            bytesAddressPair = UDPServerSocket.recvfrom(rtsp_bufferSize)
            data = bytesAddressPair[0]
            data_decoded = OlyPacket()
            data_decoded = data_decoded.decode(data)

            server_worker_port = RTP_PORT + data_decoded.payload['ssrc']
            print("server_worker_port -> " + str(server_worker_port))

            # Dar setup, correr server worker na porta RTP_Port + ssrc
            if data_decoded.flag == 'SETUP':
                rtspSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
                rtspSocket.bind(('',server_worker_port))
                clientInfo = {}
                clientInfo['rtspSocket'] = rtspSocket
                ServerWorker(clientInfo,neighbours[0]["node_ip"],RTP_PORT).run()

            # Redirecionar o pacote de dados para o pacote em que o o server worker está à escuta
            UDPClientSocket.sendto(data,('',server_worker_port))
