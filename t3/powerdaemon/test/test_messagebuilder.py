#testsuite for message builder

from mock import Mock, call, patch, MagicMock
from twisted.internet import defer, reactor
from twisted.trial import unittest

import messagebuilder

class RDPMessageTestSuite(unittest.TestCase):

	def setUp(self):
		pass

	def tearDown(self):
		reload(messagebuilder)

	def testCreateMessageObject(self):
		msg = "NOF yayayaya NOR 600"
		
		msgobject = messagebuilder.RDPMessage(msg)

		self.assertEqual(msgobject.type, "NOF")
		self.assertEqual(msgobject.identifier, "yayayaya")
		self.assertEqual(msgobject.command, "NOR")
		self.assertEqual(msgobject.descriptor, "600")

	def testCreateUpdateMessage(self):
		info = "jsonupdated"
		msg ="UPD dummytimestamp INF %s" % info

		ret = messagebuilder.RDPMessage.updateMessage(info)

		self.assertEqual(ret,msg)

	def testCreateAckMessage(self):
		identifier = "somestring"
		cmd = "POW"
		payload = "somepayload"
		msg = "ACK %s %s %s" % (identifier, cmd, payload)

		ret = messagebuilder.RDPMessage.ackMessage(identifier, cmd, payload)

		self.assertEqual(ret, msg)

	def testNormalShutdownNotif(self):
		dummymsg = "normalshutdown"
		time = 10
		msg = "NOF %s NOR %s" % (dummymsg, str(time))

		ret = messagebuilder.RDPMessage.normalShutdownMsg(dummymsg, time)

		self.assertEqual(ret, msg)	