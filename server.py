import threading
import time
import socket
import os
from datetime import datetime
from datetime import timedelta

import morsepacket

port = 60001              #port to listen for signals from
remoteConnection = None   #connection received from socket.accept()
remoteAddress = None      #address received from socket.accept()
sourceIp = "127.0.0.1"    #ip address of host. set to default value
recvSocket = None         #socket to accept connections. Called like recvSocket.accept()
events = None             #event list to replay at the right time
firstMessageTime = None   #timedelta when first message from remote was received
delay = 3                 #number of seconds to delay the playback of received morse messages
firstSendTime = None      #local datetime when the first message was sent to the remote

startTime = datetime.now()

class Client:
	def __init__(self, remoteConnection, remoteAddress):
		self.remoteConnection = remoteConnection
		self.remoteAddress = remoteAddress

class Server:
	def __init__(self):
		self.shouldQuit = False
		self.sourceIp = None
		self.recvSocket = None
		self.remoteConnection = None
		self.firstMessageTime = None
		self.clients = None
		self.listenerThread = None

	def clientThread(self, client):
		print("Started client thread.")
		try:
			remoteMessage = remoteConnection.recv(1024)
			if(firstMessageTime == None):
				firstMessageTime = datetime.now() - startTime
			morsePacket = morsepacket.MorsePacket(remoteMessage)
			addNewEvent(morsePacket)
		except Exception:
			remoteMessage = ""

	###########################################################
	# Loop and wait for new clients to connect.
	###########################################################
	def listenerThreadFunc(self):	

		clientArgs = []

		while( self.shouldQuit == False):
			self.recvSocket = socket.socket()
			self.recvSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			self.recvSocket.bind((sourceIp,port))
			self.recvSocket.listen(1)
			self.remoteConnection, self.remoteAddress = self.recvSocket.accept()
			print("Client connected.")
			client = Client(self.remoteConnection, self.remoteAddress)
			clientArgs = []
			self.clients = []
			self.clients.append(client)
			clientArgs.append(client)
			t = threading.Thread(target=self.clientThread,args=clientArgs).start()

	def startServerThread(self):
		self.listenerThread = threading.Thread(target=self.listenerThreadFunc).start()

	def close(self):
		if(self.remoteConnection != None):
			self.remoteConnection.close()
		#if connection hadn't been made yet, make a bogus one to kill socket.accept()
		if(self.recvSocket != None and self.remoteConnection == None):
			tempSock = socket.socket()
			tempSock.connect(("127.0.0.1", port))
			tempSock.close()

###########################################################
# Main method
###########################################################
def main(args):

	clients = None  #array of clients, represented by address
	remoteMessage = None
	morsePacket = None
	server = None

	if(len(args) != 2):
		print("Must provide Souce and Destination IP address as argument.")
		print("usage: python server.py <source>")
		os.sys.exit(1)

	#Get ip address argument
	sourceIp = os.sys.argv[1]

	#start server
	server = Server()
	server.startServerThread()

	print("Press enter to quit.")
	userinput = input()

	server.close()

main(os.sys.argv)
