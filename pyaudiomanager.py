import pyaudio
import math
import numpy as np

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
		p = pyaudio.PyAudio()

		volume = 1.0     # range [0.0, 1.0]
		fs = 44100       # sampling rate, Hz, must be integer
		duration = 0.10  # in seconds, may be float
		f = 880.0        # sine frequency, Hz, may be float

		# generate samples, note conversion to float32 array
		samples = (np.sin(2*np.pi*np.arange(fs*duration)*f/fs)).astype(np.float32)

		self.localSound = samples*volume

		f = 1600.0
		samples = (np.sin(2*np.pi*np.arange(fs*duration)*f/fs)).astype(np.float32)

		self.remoteSound = samples*volume

		# for paFloat32 sample values must be in range [-1.0, 1.0]
		self.localMorseStream = p.open(format=pyaudio.paFloat32,
				channels=1,
				rate=fs,
				output=True)

		# for paFloat32 sample values must be in range [-1.0, 1.0]
		self.remoteMorseStream = p.open(format=pyaudio.paFloat32,
				channels=1,
				rate=fs,
				output=True)
