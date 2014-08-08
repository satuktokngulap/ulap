#unit test for model classes
#author: Gene Paul Quevedo

from mock import Mock, call, patch, MagicMock
from twisted.internet import defer, reactor
from twisted.trial import unittest

from powermodels import ThinClient

class ThinClientTestsuite(unittest.TestCase):
	def setUp(self):
		pass

	def tearDown(self):
		pass

	def testThinClientconstructor(self):
		mac = 'fa:16:3e:2e:cd:84'
		ip = '10.225.3.233'
		comb = (ip, mac)

		thinClient = ThinClient(comb)
		self.assertEqual(thinClient.macAddress, mac)
		self.assertEqual(thinClient.ipAddress, ip)

