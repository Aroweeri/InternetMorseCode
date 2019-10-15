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
	def __init__(self, remoteConnection, remoteAddress, username):
		self.remoteConnection = remoteConnection
		self.remoteAddress = remoteAddress
		self.username = username
	def close(self):
		self.remoteConnection.close()

class Server:
	def __init__(self, sourceIp):
		self.shouldQuit = False
		self.sourceIp = sourceIp
		self.port = 60001
		self.recvSocket = None
		self.firstMessageTime = None
		self.clients = None
		self.listenerThread = None

	def clientThread(self, client):
		remoteMessage = None
		clientShouldQuit = False
		client.remoteConnection.settimeout(1);

		#get user information
		while(remoteMessage == None and clientShouldQuit == False):
			remoteMessage = client.remoteConnection.recv(1024)
			client.username = remoteMessage.decode()

		while(clientShouldQuit == False):
			try:
				remoteMessage =  client.remoteConnection.recv(1024)

				#if client disconnected, endless recv loop
				if(remoteMessage.decode() == ""):
					for c in self.clients:
						if(c.username == client.username):
							self.clients.remove(c)
					clientShouldQuit = True
					continue

				#find clients to echo message to
				for c in self.clients:
					if(c.username == client.username):
						continue
					c.remoteConnection.send(remoteMessage)
			except Exception as e: 
				if(e.__class__.__name__ == "timeout"):
					remoteMessage = ""
				elif isinstance(e, OSError):
					print("OSError exception, exiting...")
					clientShouldQuit = True

	###########################################################
	# Loop and wait for new clients to connect.
	###########################################################
	def listenerThreadFunc(self):	

		clientArgs = []

		self.recvSocket = socket.socket()
		self.recvSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.recvSocket.bind((self.sourceIp,self.port))
		self.recvSocket.listen(1)
		self.clients = []

		while( self.shouldQuit == False):
			remoteConnection, remoteAddress = self.recvSocket.accept()
			if(self.shouldQuit == True):
				return
			client = Client(remoteConnection, remoteAddress, None)
			clientArgs = []
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
	server = None

	if(len(args) != 2):
		print("Must provide Souce and Destination IP address as argument.")
		print("usage: python server.py <source>")
		os.sys.exit(1)

	#Get ip address argument
	sourceIp = os.sys.argv[1]

	#start server
	server = Server(sourceIp)
	server.startServerThread()

	print("Press enter to quit.")
	userinput = input()

	server.close()

main(os.sys.argv)
