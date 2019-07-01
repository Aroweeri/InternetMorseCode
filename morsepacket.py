from datetime import timedelta

class MorsePacket:

	eventType = None
	eventTime = None

	def __init__(self, unparsedMessage):
		self.eventType = unparsedMessage.decode().split(',')[0]
		self.eventTime = unparsedMessage.decode().split(',')[1]
		hours = self.eventTime.split(':')[0]
		minutes = self.eventTime.split(':')[1]
		seconds = self.eventTime.split(':')[2].split('.')[0]
		microseconds = self.eventTime.split('.')[1]
		self.eventTime = timedelta(days=0,hours=int(hours),minutes=int(minutes),seconds=int(seconds),microseconds=int(microseconds))

	def getEventType(self):
		return self.eventType

	def getEventTime(self):
		return self.eventTime

	def setEventTime(self, eventTime):
		self.eventTime = eventTime
