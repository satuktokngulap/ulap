#TestSuite for DBHandler

from mock import Mock, call, patch, MagicMock
from twisted.internet import defer, reactor
from twisted.trial import unittest

import dbhandler
import sqlite3

from powermodels import ThinClient, Conf


class DBHandlertestSuite(unittest.TestCase):

	def setUp(self):
		self.dbfile = '/users/genepaulquevedo/ulap/t3\
			/powerdaemon/test/artifacts/testdb.sql'
		dbhandler.DBHandler.cursor = Mock()


	def tearDown(self):
		reload(dbhandler)

	@patch('dbhandler.sqlite3')
	def testOpenDB(self, sqlite):

		dbhandler.DBHandler.openDB(self.dbfile)

		sqlite.connect.assert_called_with(self.dbfile)
		self.assertEqual(dbhandler.DBHandler.conn, sqlite.connect())
		self.assertEqual(dbhandler.DBHandler.cursor, dbhandler.DBHandler.conn.cursor())
	
	@patch('dbhandler.sqlite3')
	def testOpenDBFromConfig(self, sqlite):
		dbhandler.DBHandler.openDBFromConfigFile()

		sqlite.connect.assert_called_with(Conf.MAPFILE)

	@patch('dbhandler.sqlite3')
	def testOpenDBFromConfig_createConnection(self, sqlite):
		dbhandler.DBHandler.openDBFromConfigFile()

		self.assertEqual(dbhandler.DBHandler.conn, sqlite.connect())

	@patch('dbhandler.sqlite3')
	def testOpenDBFromConfig_createcursor(self, sqlite):
		dbhandler.DBHandler.openDBFromConfigFile()

		self.assertEqual(dbhandler.DBHandler.cursor, sqlite.connect().cursor())

	@patch('dbhandler.sqlite3')
	def testCommit(self, sqlite):
		dbhandler.DBHandler.conn = Mock()
		dbhandler.DBHandler.conn.commit = Mock()

		dbhandler.DBHandler.commit()

		assert dbhandler.DBHandler.conn.commit.called

	def testCloseDB(self):
		pass

	testCloseDB.skip = "not implemented"

	def testInsert(self):
		table = 'sampletable'
		data = ('sampledata', 1, 2.3)
		placeholder = "?,?,?,"
		dbhandler.DBHandler.cursor = Mock()
		query = "INSERT INTO sampletable VALUES (?,?,?)"

		#assumes correct table, format and data	
		dbhandler.DBHandler.insert(table, data)

		dbhandler.DBHandler.cursor.execute.assert_called_with(query, data)

	# def testUpdate(self):
	# 	table = 'sampletable'
	# 	columns = ('name', 'age', 'amount')
	# 	data = ('sampledata', 1, 2.3)
	# 	values = None # to be edited

	# 	query = """
	# 		UPDATE TABLE sampletable
	# 		SET name=(?) age=(?) amount=(?)
	# 		WHERE name=(?)
	# 		"""
	# 	dbhandler.DBHandler.updateModel(table, columns, data)

	# 	cursor.execute.assert_called_with(query, values)


	# def testRetrieveByPrimary(self):
	# 	table = 'sampletable'
	# 	column = 'amount'
	# 	data = 2.65
	# 	values = None

	# 	query = """
	# 		SELECT * FROM sampletable WHERE amount=(?)
	# 		"""
	# 	dbhandler.DBHandler.updateModel(table, column, data)

	# 	cursor.execute.assert_called_with(query, values)


	# def testSelect(self):
	# 	pass

	# def testCommit(self):
	# 	pass

	# def testConvertThinClient(self):
	# 	pass

	# def testAdapatThinClient(self):
	# 	pass

class ThinClientHandlerTestSuite(unittest.TestCase):


	def setUp(self):
		dbhandler.DBHandler.cursor = Mock()
		self.cursor = dbhandler.DBHandler.cursor

	def tearDown(self):
		reload(dbhandler)

	def testUpdateThinClientWithPort_IPAndMac(self):
		query = "UPDATE thinclient SET \
			ipaddress=:ipaddress \
			,macaddress=:macaddress \
			,sessionid=:sessionid \
			WHERE portnum=:portnum"
		port = 11
		ipaddress ="10.234.1.2"
		macaddress="as:12:we:34:rt:23"
		sessionid=None
		data = {"ipaddress": ipaddress, "macaddress": macaddress, "portnum": port, "sessionid": None}

		dbhandler.ThinClientHandler.updateThinClientWithPort(ipaddress, macaddress, port, sessionid)

		dbhandler.DBHandler.cursor.execute.assert_called_with(query, data)

	def testAddThinClient(self):
		dbhandler.DBHandler.commit = Mock()
		dbhandler.DBHandler.insert = Mock()
		thinclient = Mock()
		thinclient.ipAddress = '10.18.221.218'
		thinclient.port = 16
		thinclient.macAddress = 'as:12:we:34:rt:23'
		data = (thinclient.ipAddress, thinclient.macAddress, thinclient.port)

		dbhandler.ThinClientHandler.addThinClient(thinclient)

		dbhandler.DBHandler.insert.assert_called_with('thinclient', data)

	testAddThinClient.skip = "newer unit test exist"

	def testAddThinClient_commitChange(self):
		dbhandler.DBHandler.insert = Mock()
		dbhandler.ThinClientHandler.getThinClient = Mock(return_value=None)
		thinclient = Mock()
		dbhandler.DBHandler.commit = Mock()

		dbhandler.ThinClientHandler.addThinClient(thinclient)

		assert dbhandler.DBHandler.commit.called

	def testAddThinClient_EntryDoesntExist(self):
		dbhandler.DBHandler.insert = Mock()
		dbhandler.ThinClientHandler.getThinClient = Mock(return_value=None)
		dbhandler.DBHandler.commit = Mock()
		thinclient = Mock(port=16,ipAddress='10.18.221.218',macAddress='as:12:we:34:rt:23')
		data = (thinclient.ipAddress, thinclient.macAddress, thinclient.port)

		dbhandler.ThinClientHandler.addThinClient(thinclient)

		dbhandler.DBHandler.insert.assert_called_with('thinclient', data)

	def testAddThinClient_EntryAlreadyExists(self):
		oldTC = Mock()
		dbhandler.ThinClientHandler.getThinClient = Mock(return_value=oldTC)
		dbhandler.DBHandler.commit = Mock()
		thinclient = Mock(port=16,ipAddress='10.18.221.218',macAddress='as:12:we:34:rt:23')
		dbhandler.ThinClientHandler.updateThinClientWithPort = Mock()

		dbhandler.ThinClientHandler.addThinClient(thinclient)

		dbhandler.ThinClientHandler.updateThinClientWithPort.assert_called_with\
			('10.18.221.218', 'as:12:we:34:rt:23', 16)


	def testAddThinClient_WrongTCObject(self):
		pass

	testAddThinClient_WrongTCObject.skip = "TODO"

	def testRemoveThinClient_byPort(self):
		dbhandler.DBHandler.commit = Mock()
		thinclient = Mock()
		thinclient.ipAddress = '10.18.221.218'
		thinclient.port = 16
		thinclient.macAddress = 'as:12:we:34:rt:23'
		query = "DELETE FROM thinclient \
			WHERE portnum=:portnum"
		data = {"portnum": thinclient.port}

		dbhandler.ThinClientHandler.removeThinClient(thinclient)

		dbhandler.DBHandler.cursor.execute.assert_called_with(query, data)

	def testRemoveThinClientbyPort_commitChange(self):
		thinclient = Mock()
		dbhandler.DBHandler.commit = Mock()

		dbhandler.ThinClientHandler.removeThinClient(thinclient)

		assert dbhandler.DBHandler.commit.called

	def testGetThinClientWithPort(self):
		port = 7
		self.cursor.execute = Mock()
		query = "SELECT * FROM thinclient WHERE portnum=:portnum"
		data = {"portnum": port}

		dbhandler.ThinClientHandler.getThinClientWithPort(port)

		self.cursor.execute.assert_called_with(query, data)

	testGetThinClientWithPort.skip = "not needed"

	@patch('dbhandler.ThinClient')
	def testGetThinClient_byPort(self, thinclient):
		query = "SELECT * FROM thinclient WHERE portnum=:portnum"
		port = 5
		row = [(u'10.25.124.111', u'as:12:we:34:rt:23', 5)]
		ipaddress = '10.25.124.111'
		macaddress = 'as:12:we:34:rt:23'
		dbhandler.DBHandler.cursor.execute = MagicMock()
		dbhandler.DBHandler.cursor.execute.return_value = row		
	
		tc = dbhandler.ThinClientHandler.getThinClient(port)

		thinclient.assert_called_with((ipaddress, macaddress), port)





