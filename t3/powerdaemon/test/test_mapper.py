#Unit Test for Mapper class

from mock import Mock, call, patch, MagicMock
from twisted.internet import defer, reactor
from twisted.trial import unittest

import mapper

import subprocess, shlex

from powermodels import ThinClient

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
		mapper.Mapper.getTouple = Mock(return_value=defer.succeed(('10.225.1.1', '40:d8:55:0c:11:0a')))
		mapper.Mapper.getDHCPDetails = Mock(return_value=defer.succeed(None))
		portnum = 1

		d = mapper.Mapper.addNewThinClient(portnum)

		thinclient.assert_called_with(('10.225.1.1','40:d8:55:0c:11:0a'), portnum)
		self.assertEqual(mapper.Mapper.thinClientsList[0], thinclient())
		assert mapper.Mapper.getDHCPDetails.called 

	testAddNewThinClient.skip = 'change to callback style'

	#TODO: separate into 4 unit tests
	@patch('mapper.ThinClientHandler')
	def testAddNewThinClient(self, tchandler):
		mapper.Mapper.getTouple = Mock(return_value=defer.succeed(('10.225.1.1', '40:d8:55:0c:11:0a')))
		mapper.Mapper.getDHCPDetails = Mock(return_value=defer.succeed(None))
		mapper.Mapper.addTCToList = Mock(return_value=defer.succeed('begin'))
		tchandler.addThinClient = Mock(return_value=defer.succeed('end'))
		portnum = 9

		d = mapper.Mapper.addNewThinClient(portnum)

		d.addCallback(self.assertEqual, 'end')



	#wrapper for dhcpd parser. Output: ipaddress,mac-address tuple
	@patch('mapper.utils')
	def testGetDHCPDetails(self, utils):
		cmd = '/usr/bin/ssh' 
		params = ' -o "StrictHostKeyChecking no" root@10.18.221.21 "python /opt/lease_parser.py"'
		params = shlex.split(params)
		utils.getProcessOutput = Mock(return_value=defer.succeed(None))

		d = mapper.Mapper.getDHCPDetails()

		utils.getProcessOutput.assert_called_with(cmd, params)
		d.addCallback(self.assertEqual, None)

	@patch('mapper.os')
	@patch('__builtin__.open')
	def testGetTouple_fileRemoved(self, fileopen, os):
		TCID = '172.16.1.10,40:d8:55:0c:11:0a'
		fileopen().readline = Mock(return_value=TCID)

		ret = mapper.Mapper.getTouple()

		os.remove.assert_called_with('/tmp/touple')

	testGetTouple_fileRemoved.skip = "not performed"
	
	@patch('mapper.os')
	@patch('__builtin__.open')
	def testGetTouple_returnDeferred(self, fileopen, os):
		TCID = '172.16.1.10,40:d8:55:0c:11:0a'
		tupleID = ('172.16.1.10','40:d8:55:0c:11:0a')
		# fileopen().readline = Mock(return_value=TCID)

		d = mapper.Mapper.getTouple((TCID))

		d.addCallback(self.assertEqual, tupleID)
	
	@patch('mapper.ThinClient')
	def testAddTCToList_correctObject(self, tc):
		touple = ('10.18.221.25', '40:d8:55:0c:11:0a')
		port = 8

		d = mapper.Mapper.addTCToList(touple, port)

		self.assertEqual(mapper.Mapper.thinClientsList[0], tc())

	@patch('mapper.ThinClient')
	def testAddTCToList_correctParams(self, tc):
		touple = ('10.18.221.25', '40:d8:55:0c:11:0a')
		port = 8
		
		d = mapper.Mapper.addTCToList(touple, port)

		tc.assert_called_with(touple, port)
	
	@patch('mapper.ThinClient')
	@patch('mapper.defer')
	def testAddTCToList_returnTCObject(self, defer, tc):
		touple = ('10.18.221.25', '40:d8:55:0c:11:0a')
		port = 8

		d = mapper.Mapper.addTCToList(touple, port)

		d.addCallback(self.assertEqual, tc())


	#should not happen since thinclient is deleted as soon as it is disconnected
	@patch('mapper.ThinClient')
	def testAddTCToList_sameThinClient(self, tc):
		pass

	@patch('mapper.ThinClientHandler')
	def testRemoveThinClient(self, tchandler):
		portnum = 7
		tc = Mock()
		tc.port = portnum
		mapper.Mapper.thinClientsList = [tc]

		mapper.Mapper.removeThinClient(portnum)

		self.assertEqual(len(mapper.Mapper.thinClientsList), 0)

	@patch('mapper.ThinClientHandler')
	def testRemoveThinClient_removeFromDB(self, tchandler):
		portnum = 7
		tc = Mock()
		tc.port = portnum
		mapper.Mapper.thinClientsList = [tc]

		mapper.Mapper.removeThinClient(portnum)

		tchandler.removeThinClient.assert_called_with(tc)


	@patch('mapper.ThinClient')
	def testAddNullThinClient(self, tc):
		portnum = 6

		mapper.Mapper.addNullThinClient(portnum)

		# tc = mapper.Mapper.thinClientsList[-1]
		tc.assert_called_with((None,None), portnum)		

	def testResetLeases(self):
		#note: Mgmt VM will not start right away
		pass	

	#pass
	def testSearchByMacAddress(self):
		pass

	#pass
	def testSearchBySessionID(self):
		pass

