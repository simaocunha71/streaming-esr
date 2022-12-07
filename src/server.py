import sys, socket
import datetime

from ServerWorker import ServerWorker


class Server:

	def oly_handler(self,bytesAddressPair,neighbours):
			ip = bytesAddressPair[1][0]
		    msg = bytesAddressPair[0]

		    olypacket = OlyPacket()
		    olypacket = olypacket.decode(msg)

			if olypacket.flag == "HR":
				# Recebe vizinhos do bootstrapper
				neighbours = olypacket.payload


				# Cria mensagem de proba
				probe_message = OlyPacket()
				timestamp = datetime.now()
				saltos = 0
				data = [timestamp,saltos]
				probe_message.encode("P",data)

				 # Envia mensagem de proba para o vizinho
				UDPClientSocket.sendto(probe_message,(neighbours[0]['node_ip'],neighbours[0]['port']))

	def oly_service(self,bs_ip):
		UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

		my_ip = socket.gethostbyname(socket.gethostname())

	    UDPServerSocket.bind((my_ip,0))

	    port = UDPServerSocket.getsockname()[1]

	    # O nodo tem que mandar uma menssagem de registo
	    hello_packet = OlyPacket()
	    encoded_packet = hello_packet.encode("H",port)

	    UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
	    UDPClientSocket.sendto(encoded_packet, bootstrapperAddressPort)

		# Servidor fica à escuta de OlyPackets
	    while(True):
	        bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)

	        # Aqui chamamos um handler para interpretar a msg e agir de acordo
	        thread = Thread(target=Server.oly_handler,args=(bytesAddressPair,neighbours))
	        thread.start()

	    os._exit(0)



	def rtp_service(self):
		try:
			SERVER_PORT = int(sys.argv[2])
		except:
			print("[Usage: Server.py Server_port]\n")
		rtspSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		my_ip = socket.gethostbyname(socket.gethostname())

		rtspSocket.bind((my_ip,SERVER_PORT))
		rtspSocket.listen(5)

		# Receive client info (address,port) through RTSP/TCP session
		while True:
			clientInfo = {}
			clientInfo['rtspSocket'] = rtspSocket.accept()
			ServerWorker(clientInfo).run()

if __name__ == "__main__":

	# Recebe o ip do bootstrapper, escuta porOlypackets
	Server().oly_service(sys.argv[1])
	# Escuta por pacotes RTP
    (Server()).rtp_service()
