import sys
from tkinter import Tk
from client import Client
from OlyPacket import OlyPacket

RTP_PORT = 9999
OLY_PORT = 5555

if __name__ == "__main__":
	try:
		bootstrapperAddr = sys.argv[1]
		fileName = sys.argv[2]
	except:
		print("[Usage: ClientLauncher.py bootstrapperAddr Video_file]\n")

	print("------------CLI------------")
	# Cliente envia mensagem de Hello ao bootstrapper para saber a quem se ligar
	UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

	hello_packet = OlyPacket()
    encoded_packet = hello_packet.encode("H","")

    UDPClientSocket.sendto(encoded_packet,(bootstrapperAddr,OLY_PORT))

	# Recebe respostas do bootstrapper
	bytesAddressPair = UDPClientSocket.recv(1024)

	hello_response_packet = OlyPacket()
    hello_response_packet = hello_response_packet.decode(bytesAddressPair[0])

	# Vizinho do cliente
	neighbours = hello_response_packet.payload
	
	print("Vizinhos")
	print(neighbours)



	root = Tk()

	# Create a new client
	app = Client(root, neighbours[0]['node_ip'], RTP_PORT, RTP_PORT, fileName)
	app.master.title("RTPClient")
	root.mainloop()
