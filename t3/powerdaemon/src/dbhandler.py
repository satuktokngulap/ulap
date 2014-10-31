#Static class for handling sqlite DB operations
#author: Gene Paul L. Quevedo

import sqlite3
import logging

from powermodels import ThinClient, Conf

class DBHandler():

	#sqlite connection object
	conn = None
	cursor = None
	
	@classmethod
	def openDB(cls, dbfile):
		logging.debug("custom DB File opened")
		cls.conn = sqlite3.connect(dbfile) 
		cls.cursor = cls.conn.cursor()

	@classmethod
	def openDBFromConfigFile(cls):
		cls.conn = sqlite3.connect(Conf.MAPFILE)
		cls.cursor = cls.conn.cursor()

	#assumes correct data length. Needs exception handling later
	@classmethod
	def insert(cls, table, data):
		logging.debug("insert operation performed for table %s" % table)
		numvalues = len(data)
		query = "INSERT INTO %s VALUES (" % table 
		for n in range(numvalues):
			query = query+"?,"
		query = query[:-1]
		query = query+")"
		cls.cursor.execute(query,data)

	@classmethod
	def update(cls, table, data):
		pass

	@classmethod
	def commit(cls):
		cls.conn.commit()

	@classmethod
	def close():
		pass

class ThinClientHandler(DBHandler):

	
	@classmethod
	def updateThinClientWithPort(cls, ipaddress, macaddress, port, sessionid=None):
		logging.debug("updating DB entry for ThinClient with port %d" % port)
		data = {"ipaddress": ipaddress , "macaddress": macaddress, "portnum": port, "sessionid": sessionid }
		query = "UPDATE thinclient SET \
			ipaddress=:ipaddress \
			,macaddress=:macaddress \
			,sessionid=:sessionid \
			WHERE portnum=:portnum"

		cls.cursor.execute(query, data)

	#recieves thinclient object
	@classmethod
	def addThinClient(cls, thinclient):
		tc = cls.getThinClient(thinclient.port)
		if tc is None:
			logging.debug("new TC entry, adding to DB")
			data = (thinclient.getIPAddress(), thinclient.getMacAddress(), thinclient.getSwitchPoEPort(), thinclient.getSessionID())
			cls.insert("thinclient", data)
		else: 
			logging.debug("existing entry, updating db instead")
			cls.updateThinClientWithPort(thinclient.getIPAddress(), thinclient.getMacAddress(), thinclient.getSwitchPoEPort()\
					,thinclient.getSessionID())

		cls.commit()

	@classmethod
	def removeThinClient(cls, thinclient):
		logging.debug("removing thinClient on DB")
		query = "DELETE FROM thinclient \
			WHERE portnum=:portnum"
		data = {"portnum": thinclient.port}

		cls.cursor.execute(query, data)
		cls.commit()

	@classmethod
	def getThinClient(cls, port):
		logging.debug("retrieving thinclient with port %d" % port)
		query = "SELECT * FROM thinclient WHERE portnum=:portnum"
		tc = None
		TClist = cls.cursor.execute(query, {"portnum": port})
		for row in TClist:
			if row[2] == port:
				tc = ThinClient((str(row[0]), str(row[1])), row[2])
				break
		return tc




