import sys, socket
from datetime import datetime

import time
from threading import Thread
from OlyPacket import OlyPacket
from ServerWorker import ServerWorker

OLY_BUFFER_SIZE = 250

OLY_PORT = 5555
RTP_PORT = 9999

PERIODIC_MONITORIZATION_TIME = 10 #segundos

def sendProbeMessage(server_ip, node_ip):
    while True:
        # Cria mensagem de proba
        probe_message = OlyPacket()
        timestamp = datetime.now().strftime('%H:%M:%S.%f')
        print(timestamp)
        saltos = 0
        data = [timestamp,saltos,server_ip]
        probe_message = probe_message.encode("P",data)
        print("Mensagem de proba enviada")
        # Envia mensagem de proba para o vizinho (o servidor só tem um vizinho)
        UDPClientSocket.sendto(probe_message,(node_ip,OLY_PORT))
        time.sleep(PERIODIC_MONITORIZATION_TIME)

    

if __name__ == "__main__":

    UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    UDPServerSocket.bind(('',OLY_PORT))
    bs_ip = sys.argv[1]
    filename = sys.argv[2]

    # O nodo tem que mandar uma menssagem de registo

    hello_packet = OlyPacket()
    encoded_packet = hello_packet.encode("H",[])
    UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    UDPClientSocket.sendto(encoded_packet,(bs_ip,OLY_PORT))

    bytesAddressPair = UDPServerSocket.recvfrom(OLY_BUFFER_SIZE)

    ip = bytesAddressPair[1][0]
    msg = bytesAddressPair[0]
    olypacket = OlyPacket()
    olypacket = olypacket.decode(msg)
    if olypacket.type == "HR":
        # Recebe vizinhos do bootstrapper
        data = olypacket.payload
        neighbours = data[:-1]
        server_ip = data[-1]

        print("Vizinhos")
        print(neighbours)

        Thread(target=sendProbeMessage,args=(server_ip, neighbours[0])).start() #Monitorização periódica

        ServerWorker(neighbours[0],RTP_PORT, filename, UDPServerSocket).run()
