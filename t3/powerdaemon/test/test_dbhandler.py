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

	def testCloseDB(self):
		pass

	testCloseDB.skip = "not implemented"

	def testInsert(self):
		table = 'sampletable'
		data = ('sampledata', 1, 2.3)
		placeholder = "?,?,?,"
		dbhandler.DBHandler.cursor = Mock()
		query = "INSERT INTO sampletable VALUES (?,?,?,)"

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

	def tearDown(self):
		reload(dbhandler)

	def testUpdateThinClientWithPort_IPAddress(self):
		query = "UPDATE thinclient SET \
			ipaddress=:ipaddress \
			WHERE portnum=:portnum"
		port = 11
		ipaddress ="10.234.1.2"
		data = {"ipaddress": ipaddress, "portnum": port}

		dbhandler.ThinClientHandler.updateThinClientWithPort(ipaddress, port)

		dbhandler.DBHandler.cursor.execute.assert_called_with(query, data)

	def testAddThinClient(self):
		dbhandler.DBHandler.insert = Mock()
		thinclient = Mock()
		thinclient.ipAddress = '10.18.221.218'
		thinclient.port = 16
		thinclient.macAddress = 'as:12:we:34:rt:23'
		data = (thinclient.ipAddress, thinclient.macAddress, thinclient.port)

		dbhandler.ThinClientHandler.addThinClient(thinclient)

		dbhandler.DBHandler.insert.assert_called_with('thinclient', data)

	def testRemoveThinClient_byPort(self):
		thinclient = Mock()
		thinclient.ipAddress = '10.18.221.218'
		thinclient.port = 16
		thinclient.macAddress = 'as:12:we:34:rt:23'
		query = "DELETE FROM thinclient \
			WHERE portnum=:portnum"
		data = {"portnum": thinclient.port}

		dbhandler.ThinClientHandler.removeThinClient(thinclient)

		dbhandler.DBHandler.cursor.execute.assert_called_with(query, data)

	@patch('dbhandler.ThinClient')
	def testGetThinClient_byPort(self, thinclient):
		query = "SELECT * FROM thinclient WHERE portnum=:portnum"
		port = 5
		row = [(5, u'10.25.124.111', u'as:12:we:34:rt:23')]
		ipaddress = '10.25.124.111'
		macaddress = 'as:12:we:34:rt:23'
		dbhandler.DBHandler.cursor.execute = MagicMock()
		dbhandler.DBHandler.cursor.execute.return_value = row		
		# dbhandler.DBHandler.cursor.execute.__iter__ = Mock()
		# dbhandler.DBHandler.cursor.execute().next.return_value = row

		tc = dbhandler.ThinClientHandler.getThinClient(port)

		thinclient.assert_called_with((ipaddress, macaddress), port)





