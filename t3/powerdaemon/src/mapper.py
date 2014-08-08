#Class for generating a mapping of ThinClients and their ports
#address, etc
#Author: Gene Paul L. Quevedo

from powermodels import ThinClient, MgmtVM

import subprocess, logging, shlex, os

class Mapper():

	thinClientsList = []
	

	@classmethod
	def resetLeases(cls):
		pass

	@classmethod
	def getMap(cls):
		return thinClientsList

	#initialize list using sql database present
	@classmethod
	def initializeMap(cls):
		pass

	@classmethod
	def addNewThinClient(cls):
		
		cls.getDHCPDetails()
		thinClientDetails = cls.getTouple()
		cls.thinClientsList.append(ThinClient(thinClientDetails))
		logging.debug("details of thinclient: %s %s" % (cls.thinClientsList[0].macAddress, cls.thinClientsList[0].ipAddress))


	@classmethod
	def getDHCPDetails(cls):

		mgmtIP = MgmtVM.IPADDRESS
		remotecmd = "python /opt/lease_parser.py"
		cmd = 'ssh root@%s "%s" > /tmp/touple' % (mgmtIP, remotecmd)
		args = shlex.split(cmd)
		logging.debug("parsing using command: %s" % cmd)
		p = subprocess.Popen(args)

	

	@classmethod
	def getTouple(cls):
		f = open('/tmp/touple', 'r')
		output = f.readline()
		logging.debug("output: %s" % output)
		splittedString = output.split(',')
		tupledID = (splittedString[0],splittedString[1])
		logging.debug("adding thinClient %s" % output)
		f.close()

		os.remove('/tmp/touple')

		return tupledID

	@classmethod
	def storeClientsToDB(cls):
		pass
		
