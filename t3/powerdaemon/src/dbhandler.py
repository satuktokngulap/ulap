#Static class for handling sqlite DB operations
#author: Gene Paul L. Quevedo

import sqlite3

class DBHandler():

	#sqlite connection object
	conn = None
	cursor = None
	
	@classmethod
	def openDB(cls, dbfile):
		cls.conn = sqlite3.connect(dbfile) 
		cls.cursor = cls.conn.cursor()