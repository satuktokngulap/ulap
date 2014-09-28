#testsuite for message builder

from mock import Mock, call, patch, MagicMock
from twisted.internet import defer, reactor
from twisted.trial import unittest

from messagebuilder import RDPMessage

class RDPMessageTestSuite(unittest.TestCase):

	def setUp(self):
		self.rdpmessage=RDPMessage()

	def tearDown(self):
		pass

	def testCreateMessageObject(self):
		msg = "NOF yayayaya NOR 600"
		
		msgobject = RDPMessage(msg)

		self.assertEqual(msgobject.type, "NOF")
		self.assertEqual(msgobject.identifier, "yayayaya")
		self.assertEqual(msgobject.command, "NOR")
		self.assertEqual(msgobject.descriptor, "600")

	def testCreateUpdateMessage(self):
		info = "jsonupdated"
		msg ="UPD dummytimestamp INF %s" % info

		ret = self.rdpmessage.updateMessage(info)

		self.assertEqual(ret,msg)

	def testCreateAckMessage(self):
		identifier = "somestring"
		cmd = "POW"
		payload = "somepayload"
		msg = "ACK %s %s %s" % (identifier, cmd, payload)

		ret = self.rdpmessage.ackMessage(identifier, cmd, payload)

		self.assertEqual(ret, msg)

	def testNormalShutdownNotif(self):
		dummymsg = "normalshutdown"
		time = 10
		msg = "NOF %s NOR %s" % (dummymsg, str(time))

		ret = self.rdpmessage.normalShutdownMsg(dummymsg, time)

		self.assertEqual(ret, msg)

	def testBatteryStatusMessage(self):
		payload = '\x05\x20'
		msg = "NOF batterymode LOW BAT:DRA:0x5:0x20"

		ret = self.rdpmessage.batteryStatusMessage(payload)

		self.assertEqual(ret, msg)