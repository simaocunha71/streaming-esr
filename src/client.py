from tkinter import *
import tkinter.messagebox
from PIL import Image, ImageTk
import socket, threading, os

from RtpPacket import RtpPacket
from OlyPacket import OlyPacket

CACHE_FILE_NAME = "cache"
CACHE_FILE_EXT = ".jpg"

class Client:
	#Streaming states
	INIT = 0
	READY = 1
	PLAYING = 2
	state = INIT

	#RTSP messages
	SETUP = 0
	PLAY = 1
	PAUSE = 2
	TEARDOWN = 3

	def __init__(self, master, nodeaddr,rtspSocket,rtspPort,rtpPort):
		"""Client initialization"""
		self.master = master
		self.master.protocol("WM_DELETE_WINDOW", self.handler)
		self.createWidgets()
		self.nodeAddr = nodeaddr
		self.rtspPort = int(rtspPort)
		self.rtpPort = int(rtpPort)
		self.rtspSocket = rtspSocket
		self.rtspSeq = 0
		self.requestSent = -1
		self.teardownAcked = 0
		self.frameNbr = 0

	def createWidgets(self):
		"""Build GUI."""
		# Create Setup button
		self.setup = Button(self.master, width=20, padx=3, pady=3)
		self.setup["text"] = "Setup"
		self.setup["command"] = self.setupMovie
		self.setup.grid(row=1, column=0, padx=2, pady=2)

		# Create Play button
		self.start = Button(self.master, width=20, padx=3, pady=3)
		self.start["text"] = "Play"
		self.start["command"] = self.playMovie
		self.start.grid(row=1, column=1, padx=2, pady=2)

		# Create Pause button
		self.pause = Button(self.master, width=20, padx=3, pady=3)
		self.pause["text"] = "Pause"
		self.pause["command"] = self.pauseMovie
		self.pause.grid(row=1, column=2, padx=2, pady=2)

		# Create Teardown button
		self.teardown = Button(self.master, width=20, padx=3, pady=3)
		self.teardown["text"] = "Teardown"
		self.teardown["command"] =  self.exitClient
		self.teardown.grid(row=1, column=3, padx=2, pady=2)

		# Create a label to display the movie
		self.label = Label(self.master, height=19)
		self.label.grid(row=0, column=0, columnspan=4, sticky=W+E+N+S, padx=5, pady=5)

	def setupMovie(self):
		"""Setup button handler."""
		if self.state == self.INIT:
			self.sendRtspRequest(self.SETUP)
			self.state = self.READY
			self.openRtpPort()

	def exitClient(self):
		"""Teardown button handler."""
		self.sendRtspRequest(self.TEARDOWN)
		self.master.destroy() # Close the gui window
		os.remove(CACHE_FILE_NAME + CACHE_FILE_EXT) # Delete the cache image from video
		os._exit(0)

	def pauseMovie(self):
		"""Pause button handler."""
		if self.state == self.PLAYING:
			self.sendRtspRequest(self.PAUSE)
			self.state = self.READY
			self.playEvent.set()

	def playMovie(self):
		"""Play button handler."""
		if self.state == self.READY:
			# Create a new thread to listen for RTP packets
			threading.Thread(target=self.listenRtp).start()
			self.playEvent = threading.Event()
			self.playEvent.clear()
			self.sendRtspRequest(self.PLAY)
			self.state = self.PLAYING

	def listenRtp(self):
		"""Listen for RTP packets."""
		while True:
			try:
				data = self.rtpSocket.recv(20480)
				if data:
					rtpPacket = RtpPacket()
					rtpPacket.decode(data)

					currFrameNbr = rtpPacket.seqNum()
					print("Current Seq Num: " + str(currFrameNbr))

					#if currFrameNbr > self.frameNbr: # Discard the late packet
					self.frameNbr = currFrameNbr
					self.updateMovie(self.writeFrame(rtpPacket.getPayload()))
			except:
				# Stop listening upon requesting PAUSE or TEARDOWN
				if self.playEvent.isSet():
					break

				# Upon receiving ACK for TEARDOWN request,
				# close the RTP socket
				if self.teardownAcked == 1:
					self.rtpSocket.shutdown(socket.SHUT_RDWR)
					self.rtpSocket.close()
					break

	def writeFrame(self, data):
		"""Write the received frame to a temp image file. Return the image file."""
		cachename = CACHE_FILE_NAME + CACHE_FILE_EXT
		file = open(cachename, "wb")
		file.write(data)
		file.close()

		return cachename

	def updateMovie(self, imageFile):
		"""Update the image file as video frame in the GUI."""
		photo = ImageTk.PhotoImage(Image.open(imageFile))
		self.label.configure(image = photo, height=288)
		self.label.image = photo

	def sendRtspRequest(self, requestCode):
		"""Send RTSP request to the server."""

		# Setup request
		if requestCode == self.SETUP and self.state == self.INIT:
			# Update RTSP sequence number.
			self.rtspSeq+=1

			# Write the RTSP request to be sent.
			type_request = 'SETUP'

			# Keep track of the sent request.
			self.requestSent = self.SETUP

		# Play request
		elif requestCode == self.PLAY and self.state == self.READY:
			# Update RTSP sequence number.
			self.rtspSeq+=1
			print('\nPLAY event\n')

			# Write the RTSP request to be sent.
			type_request = 'PLAY'

			# Keep track of the sent request.
			self.requestSent = self.PLAY

		# Pause request
		elif requestCode == self.PAUSE and self.state == self.PLAYING:
			# Update RTSP sequence number.
			self.rtspSeq+=1
			print('\nPAUSE event\n')

			# Write the RTSP request to be sent.
			type_request = 'PAUSE'

			# Keep track of the sent request.
			self.requestSent = self.PAUSE

		# Teardown request
		elif requestCode == self.TEARDOWN and not self.state == self.INIT:
			# Update RTSP sequence number.
			self.rtspSeq+=1
			print('\nTEARDOWN event\n')

			# Write the RTSP request to be sent.
			type_request = 'TEARDOWN'

			# Keep track of the sent request.
			self.requestSent = self.TEARDOWN


		request = OlyPacket()
		request = request.encode(type_request, {})

		# Send the RTSP request using rtspSocket.
		self.rtspSocket.sendto(request,(self.nodeAddr,self.rtspPort))
			

	def openRtpPort(self):
		"""Open RTP socket binded to a specified port."""

		# Create a new datagram socket to receive RTP packets from the server
		self.rtpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

		# Set the timeout value of the socket to 0.5sec
		self.rtpSocket.settimeout(0.5)

		try:
			# Bind the socket to the address using the RTP port given by the client user
			self.rtpSocket.bind(('',self.rtpPort))
			print('\nBind \n')
		except Exception as e:
			tkinter.messagebox.showwarning('Unable to Bind', '%s' %e)
			tkinter.messagebox.showwarning('Unable to Bind', 'Unable to bind PORT=%d' %self.rtpPort)

	def handler(self):
		"""Handler on explicitly closing the GUI window."""
		self.pauseMovie()
		if tkinter.messagebox.askokcancel("Quit?", "Are you sure you want to quit?"):
			self.exitClient()
		else: # When the user presses cancel, resume playing.
			self.playMovie()
