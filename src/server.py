import sys, socket
from datetime import datetime

from threading import Thread
from OlyPacket import OlyPacket
from ServerWorker import ServerWorker

bufferSize = 1024

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
            # Cria mensagem de proba
            probe_message = OlyPacket()
            timestamp = datetime.now()
            saltos = 0
            data = [timestamp,saltos]
            probe_message = probe_message.encode("P",data)

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

    def rtp_service(self):

        rtspSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        rtspSocket.bind(('',RTP_PORT))
        rtspSocket.listen(5)

        # Receive client info (address,port) through RTSP/TCP session
        while True:
            clientInfo = {}
            clientInfo['rtspSocket'] = rtspSocket.accept()
            ServerWorker(clientInfo).run()

if __name__ == "__main__":
    # Recebe o ip do bootstrapper
    Server().oly_service(sys.argv[1])
    # Escuta por pacotes RTP
    (Server()).rtp_service()
