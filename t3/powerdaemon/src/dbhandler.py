#Static class for handling sqlite DB operations
#author: Gene Paul L. Quevedo

import sqlite3

from powermodels import ThinClient

class DBHandler():

	#sqlite connection object
	conn = None
	cursor = None
	
	@classmethod
	def openDB(cls, dbfile):
		cls.conn = sqlite3.connect(dbfile) 
		cls.cursor = cls.conn.cursor()

	@classmethod
	def insert(cls, table, data):
		numvalues = len(data)
		query = "INSERT INTO %s VALUES (" % table 
		for n in range(numvalues):
			query = query+"?,"
		query = query+")"
		cls.cursor.execute(query,data)

	@classmethod
	def update(cls, table, data):
		pass

	@classmethod
	def close():
		pass

class ThinClientHandler(DBHandler):


	@classmethod
	def updateThinClientWithPort(cls, ipaddress, port):
		data = {"ipaddress": ipaddress , "portnum": port }
		query = "UPDATE thinclient SET \
			ipaddress=:ipaddress \
			WHERE portnum=:portnum"

		cls.cursor.execute(query, data)

	#recieves thinclient object
	@classmethod
	def addThinClient(cls, thinclient):
		data = (thinclient.ipAddress, thinclient.macAddress, thinclient.port)

		cls.insert("thinclient",data)

	@classmethod
	def removeThinClient(cls, thinclient):
		query = "DELETE FROM thinclient \
			WHERE portnum=:portnum"
		data = {"portnum": thinclient.port}

		cls.cursor.execute(query, data)

	@classmethod
	def getThinClient(cls, port):
		query = "SELECT * FROM thinclient WHERE portnum=:portnum"
		tc = None
		TClist = cls.cursor.execute(query, {"portnum": port})
		print TClist
		for row in TClist:
			if row[0] == port:
				tc = ThinClient((str(row[1]), str(row[2])), row[0])
				break
		return tc





