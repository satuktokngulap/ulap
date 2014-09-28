#Parser for Messages coming from RDP or Epoptes
#Author: Gene Paul L. Quevedo

import logging

class Command():
    #switch commands & notifications
    SHUTDOWN_IMMEDIATE = '\x05'
    AC_RESTORED = '\x02'
    KEEPALIVE = '\x04'
    SWITCHREADY = '\x06'
    BATTSTAT = '\x08'

    
    #thinclient commands & notifications
    SHUTDOWN_CANCEL = '\x09'
    SHUTDOWN_NORMAL = '\x0C'
    SHUTDOWN_REQUEST = '\x0E'
    REDUCE_POWER = '\x03'
    POSTPONE = '1'
    POENOTIF = '\x07'


    #from RDP
    RDPREQUEST ='\x0B'
    RDPSESSIONPOWER = '\x0D'
    UPDATE = '\x0A'

#this class is just a translator. There's a better way of doing this 
#w/o a need for translation. Basically messages from Epoptes and Switch
#are different
class RDPMessageParser():

	@classmethod
	def splitToken(cls):
		pass

	@classmethod
	def translateCommand(cls, message):
		logging.debug("message from RDP: %s" % message)
		options = {
			"OFF": cls.constructOFFPayload
			,"POW": cls.constructONPayload
		}

		commands = {
			"OFF": Command.RDPREQUEST
			,"POW": Command.RDPREQUEST
			,"MOVE": Command.POSTPONE
		}

		splitmsg = message.split()
		msgtype = splitmsg[0]
		command = splitmsg[2]
		payload = splitmsg[3]

		translated = (None,None)
		try:
			translated = (commands[command],options[command](payload))
		except KeyError:
			translated = (None,None)
		return translated

	@classmethod
	def constructOFFPayload(cls, port):
		payload = None

		try:
			suffix,port = port.split("$")
			payload = [chr(int(port)),'\x02']
		except ValueError:
			payload = [chr(int(port)),'\x00']
		
		return payload

	@classmethod
	def constructONPayload(cls, port):
		return[chr(int(port)),'\x01']