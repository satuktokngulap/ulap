#TestSuite for RDP Message Parser
#Author: Gene Paul L. Quevedo

from mock import Mock, call, patch, MagicMock
from twisted.internet import defer, reactor
from twisted.trial import unittest

import messageparser

class RDPMessageParserTestSuite(unittest.TestCase):

	def setUp(self):
		pass

	def tearDown(self):
		reload(messageparser)

	def testSplitToken(self):
		message="REQ 20140910105756 OFF 6"
		tokenlist = ['REQ','20140910105756', 'OFF', 6]

		ret = messageparser.RDPMessageParser.splitToken()

		self.assertEqual(ret, tokenlist)

	testSplitToken.skip = "function practically a wrapper. not needed"	

	def testTranslateCommand_OFF(self):
		message="REQ 20140910105756 OFF 6"
		hexmessage = [messageparser.Command.RDPSESSIONPOWER, '\x06', '\x00']
		messageparser.RDPMessageParser.constructOFFPayload = Mock(return_value=hexmessage)
		messageparser.RDPMessageParser.constructONPayload = Mock(return_value=hexmessage)

		ret = messageparser.RDPMessageParser.translateCommand(message)

		messageparser.RDPMessageParser.constructOFFPayload.assert_called_with('6')
	
	def testTranslateCommand_ON(self):
		message="REQ 20140910105756 POW 6"
		hexmessage = [messageparser.Command.RDPSESSIONPOWER, '\x06', '\x01']
		messageparser.RDPMessageParser.constructONPayload = Mock(return_value=hexmessage)

		ret = messageparser.RDPMessageParser.translateCommand(message)

		messageparser.RDPMessageParser.constructONPayload.assert_called_with('6')

	def testTranslateCommand_ReturnOptionAndCommand(self):
		message="REQ 20140910105756 OFF 6"
		hexmessage = [messageparser.Command.RDPSESSIONPOWER, '\x06', '\x00']
		messageparser.RDPMessageParser.constructOFFPayload = Mock(return_value=hexmessage)

		ret = messageparser.RDPMessageParser.translateCommand(message)

		self.assertEqual(ret, (messageparser.Command.RDPREQUEST,hexmessage))

	def testTranslateCommand_SessionLoginNotif_KeyError(self):
		message = "HELLO SESSION IS ALIVE"

		ret = messageparser.RDPMessageParser.translateCommand(message)

		self.assertEqual(ret, (None, None))

	def testTranslateCommand_OFFALL(self):
		message = "REQ 20140910105756 OFF ALL$6"
		hexmessage = '\x06\x02'
		messageparser.RDPMessageParser.constructOFFPayload = Mock(return_value=hexmessage)

		ret = messageparser.RDPMessageParser.translateCommand(message)

		self.assertEqual(ret, (messageparser.Command.RDPREQUEST, hexmessage))

	def testconstructOFFPayload(self):
		port = "7"
		payload = ['\x07', '\x00']

		ret = messageparser.RDPMessageParser.constructOFFPayload(port)

		self.assertEqual(ret, payload)

	def testconstructOFFPayload_OFFAll(self):
		port = "ALL$6"
		payload = ['\x06','\x02']

		ret = messageparser.RDPMessageParser.constructOFFPayload(port)

		self.assertEqual(ret, payload)


	def testconstructONPayload(self):
		port = "7"
		payload = ['\x07', '\x01']

		ret = messageparser.RDPMessageParser.constructONPayload(port)

		self.assertEqual(ret, payload)

	def testconstructOFFPayload_ONAll(self):
		pass

	testconstructOFFPayload_ONAll.skip = "TODO"


