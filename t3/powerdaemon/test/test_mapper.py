#Unit Test for Mapper class

from mock import Mock, call, patch, MagicMock
from twisted.internet import defer, reactor
from twisted.trial import unittest

import mapper

import subprocess, shlex

class MapperTestsuite(unittest.TestCase):
	def setUp(self):
		pass

	def tearDown(self):
		mapper.Mapper.thinClientsList = []
		#reloading module to remove Mock object assignments
		reload(subprocess)
		reload(mapper)

	#top level function for new updates
	#triggered by notification from switch
	#or ThinClient
	def testUpdateMap(self):
		pass

	def testInializeMap(self):
		pass

	#top level function during initial bootup
	#creates ThinClient objects.
	@patch('mapper.ThinClient')
	def testAddNewThinClient(self, thinclient):
		# mapper.Mapper.getDHCPDetails = Mock(return_value = ('10.225.1.1', '40:d8:55:0c:11:0a'))
		mapper.Mapper.getTouple = Mock(return_value = ('10.225.1.1', '40:d8:55:0c:11:0a'))
		mapper.Mapper.getDHCPDetails = Mock()

		mapper.Mapper.addNewThinClient()

		#instantiate thinclient object
		thinclient.assert_called_with(('10.225.1.1','40:d8:55:0c:11:0a'))
		#store object to mapper (for now)
		self.assertEqual(mapper.Mapper.thinClientsList[0], thinclient())
		assert mapper.Mapper.getDHCPDetails.called 

	#wrapper for dhcpd parser. Output: ipaddress,mac-address tuple
	def testGetDHCPDetails(self):
		cmd = 'ssh root@10.18.221.21 "python /opt/lease_parser.py" > /tmp/touple'
		args = shlex.split(cmd)
		subprocess.Popen = Mock()
		#subprocess.Popen().stdout.readline = Mock(return_value=TCID)

		mapper.Mapper.getDHCPDetails()

		subprocess.Popen.assert_called_with(args)
		#self.assertEqual(ret, tupleID)

	@patch('mapper.os')
	@patch('__builtin__.open')
	def testGetTouple(self, fileopen, os):
		TCID = '172.16.1.10,40:d8:55:0c:11:0a'
		tupleID = ('172.16.1.10','40:d8:55:0c:11:0a')
		fileopen().readline = Mock(return_value=TCID)

		ret = mapper.Mapper.getTouple()

		self.assertEqual(ret, tupleID)
		os.remove.assert_called_with('/tmp/touple')

	#pass
	def testSearchByMacAddress(self):
		pass

	#pass
	def testSearchBySessionID(self):
		pass

