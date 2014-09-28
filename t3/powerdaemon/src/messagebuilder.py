#message constructor for PMD RDP Communications
#Author: Gene Paul L. Quevedo

class RDPMessage():

	def __init__(self, rawmessage=None):
		if rawmessage:
			rawmessage = rawmessage.split()
			self.type = rawmessage[0]
			self.identifier = rawmessage[1]
			self.command = rawmessage[2]
			self.descriptor = rawmessage[3]

	#useless list. for refactoring
	token = [
		['NOF', 'ACK', 'UPD']\
		,[]\
		,['NOR', 'LOW', 'NOW', 'INF', 'BAT']\
		,['BAT:DRA']
		]

	@classmethod
	def updateMessage(cls, info):
		dummydate = "dummytimestamp"
		msg = "%s %s %s %s" % (cls.token[0][2],dummydate,cls.token[2][3], info)

		return msg

	@classmethod
	def ackMessage(cls, identifier, cmd, payload):
		msg = "%s %s %s %s" % (cls.token[0][1], identifier, cmd, payload)

		return msg

	@classmethod
	def normalShutdownMsg(cls, identifier, time):
		msg = "%s %s %s %s" % (cls.token[0][0], identifier, cls.token[2][0], time)

		return msg

	@classmethod
	def batteryStatusMessage(cls, payload):
		#possible out of bounds error on payload but cannot resolve here
		#better exception to be thrown
		hours = hex(ord(payload[0]))
		mins = hex(ord(payload[1]))
		msg = "%s batterymode %s %s:%s:%s" % (cls.token[0][0], cls.token[2][1], cls.token[3][0],hours, mins)

		return msg

