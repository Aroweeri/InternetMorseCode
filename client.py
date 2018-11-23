import threading
import keyboard
import time
import socket
import os
from datetime import datetime
from datetime import timedelta
from appJar import gui

import pyaudiomanager
import morsepacket

localNoiseRunning = 0     #flag is set when morse code noise is playing due to local user action
remoteNoiseRunning = 0    #flag is set when morse code noise is playing due to remote user action
port = 60001              #port to listen for signals from
remoteConnection = None   #connection received from socket.accept()
destIp = "127.0.0.1"      #if address of destination. set to default value
lastMessage = "u"         #used to prevent sending many signals when the spacebar is held down
confirmConnection = 0     #flag set if socket.connect() returns with connection
shouldNotQuit = 1         #flag set to signal main loop to exit
app = None                #gui of the program
pyAudioManager = None     #PyAudioManager instance
events = None             #event list to replay at the right time
firstMessageTime = None   #datetime when first message from remote was received
delay = 3                 #number of seconds to delay the playback of received morse messages
firstSendTime = None      #local datetime when the first message was sent to the remote

startTime = datetime.now()

###########################################################
# Modify timedelta in packet, add to list and sort list
###########################################################
def addNewEvent(morsePacket):
	global events
	global firstMessageTime
	currentIndex = 0
	insertedOutOfPlace = 0
	modified = morsePacket
	modified.setEventTime(modified.getEventTime() + timedelta(seconds=delay))
	modified.setEventTime(modified.getEventTime() + firstMessageTime)
	if(events == None or len(events) == 0):
		events = [modified]
	else:
		for event in events:
			if(event.getEventTime() >= modified.getEventTime()):
				insertedOutOfPlace = 1
				events.insert(currentIndex,modified)
				break
			currentIndex += 1
		if(insertedOutOfPlace == 0):
			events.append(modified)

###########################################################
# Start a thread running the function eventPlaybackThread()
###########################################################
def startEventPlaybackThread():
	t = threading.Thread(target=eventPlaybackThread)
	t.start()

###########################################################
# Loop and wait for the correct system time to play back the next event in events list
###########################################################
def eventPlaybackThread():
	global shouldNotQuit
	global remoteNoiseRunning
	global events
	nextEventTime = None

	while(shouldNotQuit == 1):
		dt = datetime.now()
		if(events != None and len(events) > 0):
			nextEventTime = events[0].getEventTime()
			if(nextEventTime <= (dt-startTime)):
				if(events[0].getEventType() == "u"):    #if remote signals that spacebar was released.
					killReceivedAudio()
				elif (events[0].getEventType() == "d"): #if remote signals that spacebar was pressed down.
					if(remoteNoiseRunning == 0):          #only start the audio if not already playing
						startReceivedAudioThread()
				events.pop(0)
		time.sleep(0.005)

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
	global firstSendTime

	if(firstSendTime == None):
		firstSendTime = datetime.now()
	dt = datetime.now()
	if(lastMessage == "u"):
		remoteConnection.send("d," + str(dt - firstSendTime))
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
		remoteConnection.send("u," + str(dt - firstSendTime))
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
	global pyAudioManager
	while(localNoiseRunning == 1):
		pyAudioManager.getLocalMorseStream().write(pyAudioManager.getLocalSound())

###########################################################
# Play a beep while the killLocalAudio() function has not been called
###########################################################
def startRemoteAudio():
	global pyAudioManager
	while(remoteNoiseRunning == 1):
		pyAudioManager.getRemoteMorseStream().write(pyAudioManager.getRemoteSound())

###########################################################
# Main method
###########################################################
def main():

	global confirmConnection
	global destIp
	global remoteConnection
	global shouldNotQuit
	global pyAudioManager
	global firstMessageTime

	remoteMessage = None
	morsePacket = None

	#Get ip address argument
	if(len(os.sys.argv) != 2):
		print "Must provide Souce and Destination IP address as argument."
		print "usage: python client.py <dest>"
		os.sys.exit(1)
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
	startEventPlaybackThread()

	pyAudioManager = pyaudiomanager.PyAudioManager()
	pyAudioManager.initAudioStuff()

	#programs loops forever, waiting for a message from the remote machine to play back the
	#noise to the local user.
	while(shouldNotQuit == 1):
		try:
			remoteMessage = remoteConnection.recv(1024)
			if(firstMessageTime == None):
				firstMessageTime = datetime.now() - startTime
			morsePacket = morsepacket.MorsePacket(remoteMessage)
			addNewEvent(morsePacket)
		except Exception:
			remoteMessage = ""

	pyAudioManager.close()
	remoteConnection.close()

app = gui(handleArgs=False)
app.addLabel("label", "Waiting to connect to server... click exit button to quit")
exit =    app.addButton("exit", quit)
app.thread(main)
app.go()
