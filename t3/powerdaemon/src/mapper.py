#Class for generating a mapping of ThinClients and their ports
#address, etc
#Author: Gene Paul L. Quevedo

from powermodels import ThinClient, MgmtVM
from twisted.internet import defer, utils
from dbhandler import ThinClientHandler

import subprocess, logging, shlex, os
import json

class Mapper():

    thinClientsList = []
    toupleFile = '/tmp/touple'
    jsonfile = '/tmp/map.json'

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
    def addNewThinClient(cls, portnum):
        logging.debug("adding thinclient to map")
        d = cls.getDHCPDetails()
        d.addCallback(cls.getTouple)
        d.addCallback(cls.addTCToList, portnum)
        d.addCallback(ThinClientHandler.addThinClient)
        d.addCallback(cls.sendMapToRDP)

        return d

    @classmethod
    def getDHCPDetails(cls):
        #need some grace period here
        logging.debug("getting DHCP details from DHCP Lease file")
        sshcmd = '/usr/bin/ssh'
        mgmtIP = MgmtVM.IPADDRESS
        remotecmd = "python /opt/lease_parser.py"
        cmd = '-o "StrictHostKeyChecking no" root@%s "%s"' % (mgmtIP, remotecmd)
        args = shlex.split(cmd)
        logging.debug("parsing using command: %s" % cmd)
        d = utils.getProcessOutput(sshcmd, args)

        return d
    
    @classmethod
    def getTouple(cls, touple=None):
        logging.debug("getting IP address Mac Address touple %s" % touple)
    
        if touple:
            splittedString = touple.split(',')
        tupleID = (splittedString[0],splittedString[1].rstrip())
    
        return defer.succeed(tupleID)

    #required tuple and port. only compatible for getTouple for chaining
    @classmethod
    def addTCToList(cls, tctuple, port):
        logging.debug("adding thinClient %s,%s %s" % (tctuple[0],tctuple[1], port))
        thinclient = ThinClient(tctuple, port)
        cls.thinClientsList.append(thinclient)

        return defer.succeed(thinclient)

    @classmethod
    def addNullThinClient(cls, portnum):
        cls.thinClientsList.append(ThinClient((None,None), portnum))

    @classmethod
    def removeThinClient(cls, *args, **kwargs):

        #this enables the function to be used for callbacks
        if len(args) == 2:
            portnum = args[1]
        else: 
            portnum = args[0]

        logging.debug("removing thinClient with portnum %d" % portnum)
        for tc in cls.thinClientsList:
            if tc.port == portnum:
                ThinClientHandler.removeThinClient(tc)
                cls.thinClientsList.remove(tc)

        d = cls.sendMapToRDP()
        return d

    @classmethod
    def createSerializedThinClientData(cls):
        logging.debug('creating serialized list')
        outputlist = []
        for tc in cls.thinClientsList:
            ip = tc.getIPAddress()
            mac = tc.getMacAddress()
            port = tc.getSwitchPoEPort()
            outputlist.append({'ip': ip, 'mac': mac, 'port': port})

        return outputlist

    @classmethod
    def writeDataToFile(cls, data):
        logging.debug('writing serialized list to file')
        jsonfile = open(cls.jsonfile, 'w')
        jsonfile.write(json.dumps(data, sort_keys=True, indent=4\
            ,separators=(',',':')))
        jsonfile.close()    

    @classmethod
    def sendJSONDataToRDP(cls):
        logging.debug('sending JSON file to RDP VMs on tmp folder')
        cmd = '/usr/bin/scp'
        paramsRDPa=['/tmp/map.json', 'rdpadmin@%s:/tmp' % ThinClient.SERVERA_ADDR[0]]
        paramsRDPb=['/tmp/map.json', 'rdpadmin@%s:/tmp' % ThinClient.SERVERB_ADDR[0]]
        d1 = utils.getProcessOutput(cmd, paramsRDPa)
        d2 = utils.getProcessOutput(cmd, paramsRDPb)

        d = defer.DeferredList([d1, d2])
        return d

    @classmethod
    def sendMapToRDP(cls, value=None):
        logging.debug('initiating construction of json file')
        data = cls.createSerializedThinClientData()
        cls.writeDataToFile(data)
        d = cls.sendJSONDataToRDP()

        return d

    @classmethod
    def getSessionIPGivenSessionID(cls, text, ID):
        text = text.split()
        ret = None
        for word in text:
            if word.find('UID=') >= 0:
                if word[4:] == ID:
                    ret = text[text.index(word)+2][3:]

        return ret

    @classmethod
    def getRDPSessionDetails(cls):
        cmd = '/usr/bin/ssh'
        paramsRDP1 = '-o "StrictHostKeyChecking no" root@%s "python /opt/xfinger.sh"' % ThinClient.SERVERA_ADDR[0]
        paramsRDP2 = '-o "StrictHostKeyChecking no" root@%s "python /opt/xfinger.sh"' % ThinClient.SERVERB_ADDR[0]
        paramsRDP1 = shlex.split(paramsRDP1)
        paramsRDP2 = shlex.split(paramsRDP2)

        d1 = utils.getProcessOutput(cmd, paramsRDP1)
        d2 = utils.getProcessOutput(cmd, paramsRDP2)

        d = defer.DeferredList([d1, d2])
        return d

    @classmethod
    def storeClientsToDB(cls):
        pass
        
