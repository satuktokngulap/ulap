#TestSuite for DBHandler

from mock import Mock, call, patch, MagicMock
from twisted.internet import defer, reactor
from twisted.trial import unittest

import dbhandler, sqlite3

class DBHandlertestSuite(unittest.TestCase):

	def setUp(self):
		self.dbfile = '/users/genepaulquevedo/ulap/t3\
			/powerdaemon/test/artifacts/testdb.sql'

	def tearDown(self):
		reload(dbhandler)

	@patch('dbhandler.sqlite3')
	def testOpenDB(self, sqlite):

		dbhandler.DBHandler.openDB(self.dbfile)

		sqlite.connect.assert_called_with(self.dbfile)
		self.assertEqual(dbhandler.DBHandler.conn, sqlite.connect())
		self.assertEqual(dbhandler.DBHandler.cursor, dbhandler.DBHandler.conn.cursor())

	def testCloseDB(self):
		pass

	testCloseDB.skip = "not implemented"

	def testInsert(self):
		dbhandler.DBHandler.cursor = Mock()
		table = 'sampletable'
		data = ('sampledata', 1, 2.3)
		query = """
			INSERT into ? VALUES (?,)
			"""

		#assumes correct table, format and data	
		dbhandler.DBHandler.insertModel(table, data)

		cursor.execute.assert_called_with()

	def testUpdate(self):
		pass

	def testRetrieve(self):
		pass

	def testCommit(self):
		pass

	def testConvertThinClient(self):
		pass

	def testAdapatThinClient(self):
		pass

