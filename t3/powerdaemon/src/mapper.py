#Class for generating a mapping of ThinClients and their ports
#address, etc
#Author: Gene Paul L. Quevedo

from powermodels import ThinClient, MgmtVM

import subprocess

class Mapper():

	thinClientsList = []
	
	@classmethod
	def initializeMap(cls):
		
		thinClientDetails = cls.getDHCPDetails()

		cls.thinClientsList.append(ThinClient(thinClientDetails))

	@classmethod
	def getDHCPDetails(cls):

		mgmtIP = MgmtVM.IPADDRESS
		remotecmd = "python /opt/lease_parser.py"
		cmd = 'ssh root@%s "%s"' % (mgmtIP, remotecmd)

		p = subprocess.Popen(cmd, stdout=subprocess.PIPE)

		output = p.stdout.readline()

		return output
		
