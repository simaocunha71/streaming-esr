import sys
import socket
from tkinter import Tk
from client import Client
from OlyPacket import OlyPacket

OLY_BUFFER_SIZE = 250

RTP_PORT = 9999
OLY_PORT = 5555

def Oly_handler(bytesAddressPair):
    neighbours = []
    ip = bytesAddressPair[1][0]
    msg = bytesAddressPair[0]

    olypacket = OlyPacket()
    olypacket = olypacket.decode(msg)

    # Pacote Hello Response
    if olypacket.type=="HR":
        # O payload é os vizinhos do nodo
        print("Vizinhos")
        print(olypacket.payload)
        neighbours = olypacket.payload

    return neighbours



if __name__ == "__main__":
    try:
        bootstrapperAddr = sys.argv[1]
    except:
        print("[Usage: ClientLauncher.py bootstrapperAddr]\n")

    print("------------CLI------------")
    # Cliente envia mensagem de Hello ao bootstrapper para saber a quem se ligar
    UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    UDPServerSocket.bind(('',OLY_PORT))


    hello_packet = OlyPacket()
    encoded_packet = hello_packet.encode("H",[])

    # Cliente envia mensagem de Hello ao bootstrapper para saber a quem se ligar
    UDPClientSocket.sendto(encoded_packet,(bootstrapperAddr,OLY_PORT))

    # Recebe respostas do bootstrapper

    bytesAddressPair = UDPServerSocket.recvfrom(OLY_BUFFER_SIZE)
    data = Oly_handler(bytesAddressPair)
    neighbours = data[:-1]
    #thread = Thread(target=Oly_handler,args=(bytesAddressPair))
    #thread.start()


    root = Tk()

    # Create a new client
    print(neighbours)
    app = Client(root, neighbours[0],UDPServerSocket,OLY_PORT, RTP_PORT)
    app.master.title("RTPClient")
    root.mainloop()
