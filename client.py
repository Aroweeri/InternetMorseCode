import threading
import keyboard
import math
import pyaudio
import time
import socket
import os
from datetime import datetime
from appJar import gui

localNoiseRunning = 0     #flag is set when morse code noise is playing due to local user action
remoteNoiseRunning = 0    #flag is set when morse code noise is playing due to remote user action
port = 60001              #port to listen for signals from
remoteConnection = None   #connection received from socket.accept()
destIp = "127.0.0.1"      #if address of destination. set to default value
localMorseStream = None   #audio stream to write morse code noise to signify local user action
remoteMorseStream = None  #audio stream to write morse code noise to signify remote user action
LOCALWAVEDATA = None      #sine wave sound played when local user is sending morse code
REMOTEWAVEDATA = None     #sine wave sound played when remote user is sending morse code
pyAudio = None            #pyAudio object
lastMessage = "u"         #used to prevent sending many signals when the spacebar is held down
confirmConnection = 0     #flag set if socket.connect() returns with connection
shouldNotQuit = 1         #flag set to signal main loop to exit
app = None                #gui of the program

startTime = datetime.now()

###########################################################
# Add the morse clicker and exit buttons to the gui and remove label
###########################################################
def addButtonsToGui():
	global app
	app.removeLabel("label")
	clicker = app.addButton("clicker", None)
	clicker.bind("<Button-1>", buttonPressed, add="+")
	clicker.bind("<ButtonRelease-1>", buttonReleased, add="+")

###########################################################
# Close resources and exit program properly
###########################################################
def quit(suppress):
	global shouldNotQuit
	global app
	shouldNotQuit = 0
	app.stop()

###########################################################
# Start audio with a lower noise to signify message from remote
###########################################################
def startReceivedAudioThread():
	global remoteNoiseRunning
	if(remoteNoiseRunning != 0):
		return
	remoteNoiseRunning = 1
	t = threading.Thread(target=startRemoteAudio)
	t.start()

###########################################################
# killLocalAudio audio with a lower noise to signify remote message over
###########################################################
def killReceivedAudio():
	global remoteNoiseRunning
	remoteNoiseRunning = 0

###########################################################
# Start the audio thread and send a press signal to destination
###########################################################
def buttonPressed(suppress):
	global remoteConnection
	global lastMessage
	dt = datetime.now()
	if(lastMessage == "u"):
		remoteConnection.send("d," + str(dt - startTime))
		lastMessage = "d"
		startLocalAudioThread()

###########################################################
# killLocalAudio audio thread and send a release signal to destination
###########################################################
def buttonReleased(suppress):
	global remoteConnection
	global lastMessage
	dt = datetime.now()
	if(lastMessage == "d"):
		remoteConnection.send("u," + str(dt - startTime))
		lastMessage = "u"
		killLocalAudio()

###########################################################
# Start a thread to play audio
###########################################################
def startLocalAudioThread():
	global localNoiseRunning
	if(localNoiseRunning != 0):
		return
	localNoiseRunning = 1
	t = threading.Thread(target=startLocalAudio)
	t.start()

###########################################################
# Set flag to stop running the audio thread
###########################################################
def killLocalAudio():
	global localNoiseRunning
	localNoiseRunning = 0

###########################################################
# Play a beep while the killLocalAudio() function has not been called
###########################################################
def startLocalAudio():
	global localMorseStream
	while(localNoiseRunning == 1):
		localMorseStream.write(LOCALWAVEDATA)

###########################################################
# Play a beep while the killLocalAudio() function has not been called
###########################################################
def startRemoteAudio():
	global remoteMorseStream
	while(remoteNoiseRunning == 1):
		remoteMorseStream.write(REMOTEWAVEDATA)

###########################################################
# Set up PyAudio things
# *** This section copied from online forums, modified by me.
###########################################################
def initAudioStuff():
	global pyAudio
	global localMorseStream
	global remoteMorseStream
	global LOCALWAVEDATA
	global REMOTEWAVEDATA

	#initialize pyaudio
	PyAudio = pyaudio.PyAudio

	#See https://en.wikipedia.org/wiki/Bit_rate#Audio
	BITRATE = 60000   #number of frames per second/frameset.      
	FREQUENCY = 1000  #Hz, waves per second, 261.63=C4-note.
	LENGTH = 0.05     #seconds to play sound

	NUMBEROFFRAMES = int(BITRATE * LENGTH)
	RESTFRAMES = NUMBEROFFRAMES % BITRATE
	LOCALWAVEDATA = ''    

	#generate sine waves
	for x in xrange(NUMBEROFFRAMES):
		LOCALWAVEDATA = LOCALWAVEDATA+chr(int(math.sin(x/((BITRATE/FREQUENCY)/math.pi))*127+128))

	FREQUENCY = 2000     #Hz, waves per second, 261.63=C4-note.

	NUMBEROFFRAMES = int(BITRATE * LENGTH)
	RESTFRAMES = NUMBEROFFRAMES % BITRATE
	REMOTEWAVEDATA = ''    
	#generating waves
	for x in xrange(NUMBEROFFRAMES):
		REMOTEWAVEDATA = REMOTEWAVEDATA+chr(int(math.sin(x/((BITRATE/FREQUENCY)/math.pi))*127+128))

	pyAudio = PyAudio()

	#start stream to use for local morse code noise
	localMorseStream = pyAudio.open(format = pyAudio.get_format_from_width(1),
		channels = 1,
		rate = BITRATE,
		output = True)

	#start stream to use for remote morse code noise
	remoteMorseStream = pyAudio.open(format = pyAudio.get_format_from_width(1),
		channels = 1,
		rate = BITRATE,
		output = True)

###########################################################
# Main method
###########################################################
def main():

	global confirmConnection
	global remoteConnection
	global destIp
	global shouldNotQuit
	global localMorseStream
	global remoteMorseStream

	remoteMessage = None

	#Get ip address argument
	if(len(os.sys.argv) != 2):
		print "Must provide Souce and Destination IP address as argument."
		print "usage: python keyboard_stuff.py <dest>"
		exit(1)
	else:
		destIp = os.sys.argv[1]


	#connect to remote machine. Retry indefinitely until user terminates program.
	remoteConnection = socket.socket()
	remoteConnection.settimeout(1)
	while(confirmConnection == 0):
		time.sleep(1)
		try:
			remoteConnection.connect((destIp, port))
			confirmConnection = 1
		except Exception:
			confirmConnection = 0

	addButtonsToGui()
	initAudioStuff()

	#programs loops forever, waiting for a message from the remote machine to play back the
	#noise to the local user.
	while(shouldNotQuit == 1):
		try:
			remoteMessage = remoteConnection.recv(1024)
			print(remoteMessage)
		except Exception:
			remoteMessage = ""
		if(remoteMessage == "u"):      #if remote signals that spacebar was released.
			killReceivedAudio()
		elif (remoteMessage == "d"): #if remote signals that spacebar was pressed down.
			if(remoteNoiseRunning == 0):  #only start the audio if not already playing
				startReceivedAudioThread()

	localMorseStream.stop_stream()
	localMorseStream.close()
	remoteMorseStream.stop_stream()
	remoteMorseStream.close()
	remoteConnection.close()

app = gui(handleArgs=False)
app.addLabel("label", "Waiting to connect to server... click exit button to quit")
exit =    app.addButton("exit", quit)
app.thread(main)
app.go()
