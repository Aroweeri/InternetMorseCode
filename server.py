import threading
import time
import socket
import os
from datetime import datetime
from datetime import timedelta

import morsepacket

events = None             #event list to replay at the right time
delay = 3                 #number of seconds to delay the playback of received morse messages

startTime = datetime.now()

class Client:
	def __init__(self, remoteConnection, remoteAddress):
		self.remoteConnection = remoteConnection
		self.remoteAddress = remoteAddress
	def close(self):
		self.remoteConnection.close()

class Server:
	def __init__(self):
		self.shouldQuit = False
		self.sourceIp = "127.0.0.1"
		self.port = 60001
		self.recvSocket = None
		self.firstMessageTime = None
		self.clients = None
		self.listenerThread = None

	def clientThread(self, client):
		client.remoteConnection.settimeout(1);
		while(self.shouldQuit == False):
			try:
				remoteMessage =  client.remoteConnection.recv(1024)
				for c in self.clients:
					#if(c.remoteAddress == client.remoteAddress):
					#	continue
					c.remoteConnection.send(remoteMessage)
			except Exception:
				remoteMessage = ""

	###########################################################
	# Loop and wait for new clients to connect.
	###########################################################
	def listenerThreadFunc(self):	

		clientArgs = []

		self.recvSocket = socket.socket()
		self.recvSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.recvSocket.bind((self.sourceIp,self.port))
		self.recvSocket.listen(1)

		while( self.shouldQuit == False):
			remoteConnection, remoteAddress = self.recvSocket.accept()
			if(self.shouldQuit == True):
				return
			client = Client(remoteConnection, remoteAddress)
			clientArgs = []
			self.clients = []
			self.clients.append(client)
			clientArgs.append(client)
			t = threading.Thread(target=self.clientThread,args=clientArgs).start()

	def startServerThread(self):
		self.listenerThread = threading.Thread(target=self.listenerThreadFunc).start()

	def close(self):
		self.shouldQuit = True;
		if(self.clients != None):
			for c in self.clients:
				c.close()
				c.remoteConnection.close()
		#if connection hadn't been made yet, make a bogus one to kill socket.accept()
		if(self.recvSocket != None):
			tempSock = socket.socket()
			tempSock.connect((self.sourceIp, self.port))
			tempSock.close()
		self.recvSocket.close()

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
