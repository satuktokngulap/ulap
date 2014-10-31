#Class for generating a mapping of ThinClients and their ports
#address, etc
#Author: Gene Paul L. Quevedo

from powermodels import ThinClient, MgmtVM, Session
from twisted.internet import defer, utils
from dbhandler import ThinClientHandler

import subprocess, logging, shlex, os
import json
import re

class Mapper():

    thinClientsList = []
    sessionList = []
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
            sessionid = tc.getSessionID()
            userid = cls.getUserIDGivenSessionID(sessionid)
            outputlist.append({'ip': ip, 'mac': mac, 'port': port, 'sessionid': sessionid, 'userid': userid})

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

    #unused
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
    def getUserIDGivenSessionID(cls, ID):
        userid = None
        for session in cls.sessionList:
            sessionid = session.getSessionID()
            if sessionid == ID:
                userid = session.getUserID()

        return userid

    @classmethod
    def getRDPSessionsViaXFinger(cls):
        cmd = '/usr/bin/ssh'
        paramsRDP1 = '-o "StrictHostKeyChecking no" root@%s "/opt/xfinger.sh"' % ThinClient.SERVERA_ADDR[0]
        paramsRDP2 = '-o "StrictHostKeyChecking no" root@%s "/opt/xfinger.sh"' % ThinClient.SERVERB_ADDR[0]
        paramsRDP1 = shlex.split(paramsRDP1)
        paramsRDP2 = shlex.split(paramsRDP2)

        d1 = utils.getProcessOutput(cmd, paramsRDP1)
        d2 = utils.getProcessOutput(cmd, paramsRDP2)

        d = defer.DeferredList([d1, d2])
        return d

    @classmethod
    def parseXFingerResults(cls, results):
        UIDList = []
        PIDList = []
        IPList = []
        SessionList = []
        for (success, value) in results:
            if success:
                uidresults = re.findall('(?<=UID\=)[0-9a-zA-Z]+', value)
                pidresults = re.findall('(?<=PID\=)[0-9a-zA-Z]+', value)
                ipresults  = re.findall('[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+', value)
                if len(UIDList) != len(PIDList) or len(PIDList) != len(IPList):
                    logging.error('error on xfinger results. Check xfinger script or xrdp logs')
                    #throw exception?
                else:
                    logging.debug("XRDP session parsed")
                    UIDList = UIDList + uidresults
                    PIDList = PIDList + pidresults
                    IPList = IPList + ipresults

            elif not success:
                logging.debug('failure occured when executing xFinger')

        tupledSessions = zip(UIDList,PIDList,IPList)
        for s in tupledSessions:
            sessionentry = {"sessionid": int(s[1]), "userid": s[0], "ipaddress": s[2]}
            SessionList.append(sessionentry)

        return SessionList

    @classmethod
    def updateSessionList(cls, sessionList):
        cls.sessionList = []
        for session in sessionList:
            logging.debug("adding session object to sessionlist")
            s = Session(session["sessionid"], session["userid"])
            cls.sessionList.append(s)

    #updates ThinClient on the ThinClientList w/ the appropriate session
    @classmethod
    def updateThinClientSessionAttribute(cls, session):
        for tc in cls.thinClientsList:
            ip = tc.getIPAddress()
            # logging.debug("ip on thinclient: %send" % ip)
            # logging.debug("ip on session: %send" % session["ipaddress"])
            if ip == session["ipaddress"]:
                logging.debug('modifying thinclient object')
                tc.setSessionID(session["sessionid"])

    @classmethod
    def resetSessionList(cls):
        cls.sessionList = [] 

    @classmethod
    def removeSessionsOnThinclients(cls):
        for tc in cls.thinClientsList:
            tc.setSessionID(None)

    #Top method
    @classmethod
    def updateSessions(cls):
        logging.debug("updating sessions due to login/logout event")
        cls.resetSessionList()
        cls.removeSessionsOnThinclients()
        d = cls.getRDPSessionsViaXFinger()
        d.addCallback(cls.updateSessionListAndAttributes)
        d.addCallback(cls.sendMapToRDP)

    @classmethod
    def updateSessionListAndAttributes(cls, sessionString):
        sessionList = cls.parseXFingerResults(sessionString)
        cls.updateSessionList(sessionList)
        for session in sessionList:
            cls.updateThinClientSessionAttribute(session)

    @classmethod
    def storeClientsToDB(cls):
        pass
        
