from random import randint
import sys, traceback, threading, socket

from VideoStream import VideoStream
from RtpPacket import RtpPacket

class ServerWorker:
	#RTSP messages
	SETUP = 'SETUP'
	PLAY = 'PLAY'
	PAUSE = 'PAUSE'
	TEARDOWN = 'TEARDOWN'

	#Streaming states
	INIT = 0
	READY = 1
	PLAYING = 2
	state = INIT

	#Sucess/Error codes
	OK_200 = 0
	FILE_NOT_FOUND_404 = 1
	CON_ERR_500 = 2

	clientInfo = {}

	def __init__(self,clientInfo,nodeAdrr,nodePort):
		"""Server Worker initialization"""
		self.clientInfo = clientInfo
		# Endereço e porta de atendimento do vizinho do servidor
		self.nodeAdrr = nodeAdrr
		self.nodePort = nodePort

	def run(self):
		"""Server Worker into a thread"""
		threading.Thread(target=self.recvRtspRequest).start()

	def recvRtspRequest(self):
		"""Receive RTSP request from the client."""
		connSocket = self.clientInfo['rtspSocket']
		while True:
			data = connSocket.recvfrom(256)
			if data:
				request = OlyPacket()
				request = request.decode(data)
				print("Data received:\n" + request.flag)
				self.processRtspRequest(request)

	def processRtspRequest(self, data):
		"""Process RTSP request sent from the client."""
		# Get the request type

		requestType = data.flag

		# Get the media file name
		filename = data.payload["file_name"]

		# Get the RTSP sequence number
		seq = data.payload["rtpsp_seq"]

		# Process SETUP request
		if requestType == self.SETUP:
			if self.state == self.INIT:
				# Update state
				print("processing SETUP\n")

				try:
					self.clientInfo['videoStream'] = VideoStream(filename)
					self.state = self.READY
				except IOError:
					print("FILE_NOT_FOUND_404")

				# Generate a randomized RTSP session ID
				self.clientInfo['session'] = randint(100000, 999999)

				# Send RTSP reply
				print("ok_200")

				# Get the RTP/UDP port
				self.clientInfo['rtpPort'] = data.payload["rtp_port"]

		# Process PLAY request
		elif requestType == self.PLAY:
			if self.state == self.READY:
				print("processing PLAY\n")
				self.state = self.PLAYING

				# Create a new socket for RTP/UDP
				self.clientInfo["rtpSocket"] = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

				print("ok_200")

				# Create a new thread and start sending RTP packets
				self.clientInfo['event'] = threading.Event()
				self.clientInfo['worker']= threading.Thread(target=self.sendRtp)
				self.clientInfo['worker'].start()

		# Process PAUSE request
		elif requestType == self.PAUSE:
			if self.state == self.PLAYING:
				print("processing PAUSE\n")
				self.state = self.READY

				self.clientInfo['event'].set()

				print("ok_200")

		# Process TEARDOWN request
		elif requestType == self.TEARDOWN:
			print("processing TEARDOWN\n")

			self.clientInfo['event'].set()

			print("ok_200")

			# Close the RTP socket
			self.clientInfo['rtpSocket'].close()

	def sendRtp(self):
		"""Send RTP packets over UDP."""
		while True:
			self.clientInfo['event'].wait(0.05)

			# Stop sending if request is PAUSE or TEARDOWN
			if self.clientInfo['event'].isSet():
				break

			data = self.clientInfo['videoStream'].nextFrame()
			if data:
				frameNumber = self.clientInfo['videoStream'].frameNbr()
				try:
					address = self.clientInfo['rtspSocket'][1][0]
					port = int(self.clientInfo['rtpPort'])
					self.clientInfo['rtpSocket'].sendto(self.makeRtp(data, frameNumber),(address,port))
				except Exception as e:
					print("Connection Error")
					print(e)
					print('-'*60)
					traceback.print_exc(file=sys.stdout)
					print('-'*60)

	def makeRtp(self, payload, frameNbr):
		"""RTP-packetize the video data."""
		version = 2
		padding = 0
		extension = 0
		cc = 0
		marker = 0
		pt = 26 # MJPEG type
		seqnum = frameNbr
		ssrc = 0

		rtpPacket = RtpPacket()

		rtpPacket.encode(version, padding, extension, cc, seqnum, marker, pt, ssrc, payload)

		return rtpPacket.getPacket()
