import pyaudio
import math

class PyAudioManager:
	localMorseStream = None   #audio stream to write morse code noise to signify local user action
	remoteMorseStream = None  #audio stream to write morse code noise to signify remote user action
	localSound = None         #sine wave sound played when local user is sending morse code
	remoteSound = None        #sine wave sound played when remote user is sending morse code
	pyAudio = None            #pyAudio object

	def getRemoteSound(self):
		return self.remoteSound

	def getLocalSound(self):
		return self.localSound

	def getLocalMorseStream(self):
		return self.localMorseStream

	def getRemoteMorseStream(self):
		return self.remoteMorseStream

	def close(self):
		self.localMorseStream.stop_stream()
		self.localMorseStream.close()
		self.remoteMorseStream.stop_stream()
		self.remoteMorseStream.close()

	###########################################################
	# Set up PyAudio things
	# *** This section copied from online forums, modified by me.
	###########################################################
	def initAudioStuff(self):
		#initialize pyaudio
		PyAudio = pyaudio.PyAudio

		#See https://en.wikipedia.org/wiki/Bit_rate#Audio
		BITRATE = 60000   #number of frames per second/frameset.      
		FREQUENCY = 1000  #Hz, waves per second, 261.63=C4-note.
		LENGTH = 0.05     #seconds to play sound

		NUMBEROFFRAMES = int(BITRATE * LENGTH)
		RESTFRAMES = NUMBEROFFRAMES % BITRATE
		self.localSound = ''    

		#generate sine waves
		for x in range(NUMBEROFFRAMES):
			self.localSound = self.localSound+chr(int(math.sin(x/((BITRATE/FREQUENCY)/math.pi))*127+128))

		FREQUENCY = 2000     #Hz, waves per second, 261.63=C4-note.

		NUMBEROFFRAMES = int(BITRATE * LENGTH)
		RESTFRAMES = NUMBEROFFRAMES % BITRATE
		self.remoteSound = ''    
		#generating waves
		for x in range(NUMBEROFFRAMES):
			self.remoteSound = self.remoteSound+chr(int(math.sin(x/((BITRATE/FREQUENCY)/math.pi))*127+128))

		self.pyAudio = PyAudio()

		#start stream to use for local morse code noise
		self.localMorseStream = self.pyAudio.open(format = self.pyAudio.get_format_from_width(1),
			channels = 1,
			rate = BITRATE,
			output = True)

		#start stream to use for remote morse code noise
		self.remoteMorseStream = self.pyAudio.open(format = self.pyAudio.get_format_from_width(1),
			channels = 1,
			rate = BITRATE,
			output = True)
