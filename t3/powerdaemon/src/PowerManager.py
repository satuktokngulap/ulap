#!/usr/bin/python


#Power Management Daemon
#Description: Communicates with the Switch and ThinClients for shutdown 
#requests, immediate shutdown and reduced-power operations.
#Author: Gene Paul Quevedo



import logging, os, signal, re
import time as timer
import ConfigParser

from twisted.internet import reactor, utils, task, defer
from twisted.internet import protocol
from twisted.internet.protocol import DatagramProtocol
from twisted.protocols import basic

from Crypto.Cipher import AES
from datetime import datetime, time, date, timedelta

from ipaddressfinder import IPAddressFinder
from powermodels import Conf, NodeA, NodeB, Switch, ThinClient, Power, MasterTC
from powermodels import ServerState, PowerState, SwitchState
from mapper import Mapper
from dbhandler import DBHandler
from messageparser import Command, RDPMessageParser
from messagebuilder import RDPMessage

#change on deployment
from configreader import fillAllDefaults

class IPMISecurity():
    #IPMI passwords are 16 Bytes long.
    def __init__(self):
        self.BlockSize = 16
        self.Padding = '}'
        self.secretKey = 'Pa$sW0rD'
        self.secretFile = '/var/lib/power_daemon/secret'
        self.passPhrase = None
        self.password = None


    def decrypt(self, passphrase, IV, encrypted):
        aes = AES.new(passphrase, AES.MODE_CFB, IV)
        return aes.decrypt(encrypted)   

    def encrypt(self, passphrase, IV, message):
        aes = AES.new(passphrase, AES.MODE_CFB, IV)
        return aes.encrypt(message) 

    def getIPMIPassword(self):
        IPMIpasswdfile = open(self.secretFile)
        IV = IPMIpasswdfile.readline()
        ciphertext = IPMIpasswdfile.readline()
        self.password = self.decrypt( self.secretKey, IV, ciphertext)

    def storeIPMIPassword(self):
        IV = os.urandom(self.BlockSize)
        ciphertext = self.encrypt(self.secretKey , IV, self.password)
        IPMIpasswdfile = open(self.secretFile)
        IPMIpasswdfile.write(IV)
        IPMIpasswdfile.write(ciphertext)
        IPMIpasswdfile.close()
        

class ServerNotifs():
    #notifications to ThinClients/RDP Server
    NORMAL_SHUTDOWN_START_COUNTDOWN = 0x1100000


#power manager class
class PowerManager(DatagramProtocol):
    #top-level manager class for handling power monitoring and shutdown 
    #singleton design pattern (?)
    def __init__(self):
        self.shutdownDelay = Conf.DEFAULTSCHEDULEDSHUTDOWNWAITTIME
        self.postponeToggle = False
        self.waitingForPoEConfirm = False
        self.PoECounter = 1
        self.readyPorts = 16 #default. changed at startup
        self.thinClientsInitialized = False


    def _logExitValue(self, exitValue):
        logging.info("exit value of last command:%s" % exitValue)

    def sendIPMICommand(self, *args, **kwargs):
        params = None

        logging.debug("now sending IPMI command")  
        #work around for sending param arguments for nested consecutive
        #sendIPMICommands
        if len(args) > 0:
            params = args[-1] 

        cmd = '/usr/bin/ipmitool'
        for key, value in kwargs.iteritems():
            if key=="params":
                params=value
                logging.debug(params)
                    

        d = utils.getProcessOutput(cmd, params)
        return d

    def sendPowerOffSwitchPort(self, portnum):
        params = ['-H', Switch.IPADDRESS, '-U', Switch.USERNAME\
            , '-P', Switch.PASSWORD, 'raw', '0x32', '0x38'\
                , portnum, '0x0']

        d = self.sendIPMICommand(params) 
        return d

    #Deprecated/unused
    def getPortNumberFromMac(self, mac):
        config = ConfigParser.ConfigParser()
        config.read(Conf.MACFILE)
        port = None
        for n in range(16):
            storedmac = config.get('mac', str(n))
            if mac == storedmac:
                port = n
                break
        return hex(port)

    def getCurrentTime(self):
        return datetime.today()

    def sendPowerONStatusToSwitch(self):
        params = []
        params.append('-H')
        params.append(Switch.IPADDRESS)
        params.append('-U')
        params.append(Switch.USERNAME)
        params.append('-P')
        params.append(Switch.PASSWORD)
        params.append('raw')
        params.append(Switch.OEMCMD)
        params.append(Switch.POWERONCMD)
        params = tuple(params)

        d = self.sendIPMICommand(params)
        return d

    def resetWakeup(self, value=None):
        logging.info("resetting wakeup time on switch")
        params = []
        params.append('-H')
        params.append(Switch.IPADDRESS)
        params.append('-U')
        params.append(Switch.USERNAME)
        params.append('-P')
        params.append(Switch.PASSWORD)
        params.append('raw')
        params.append('0x30')
        params.append('0x38')

        for n in range(6):
            params.append('00')

        d = self.sendIPMICommand(params)

        return d

    def sendWakeUpTime(self, value=None):
        logging.debug("sending wake up time to switch")

        params = []
        params.append('-H')
        params.append(Switch.IPADDRESS)
        params.append('-U')
        params.append(Switch.USERNAME)
        params.append('-P')
        params.append(Switch.PASSWORD)
        params.append('raw')
        params.append('0x30')
        params.append('0x38')

        datetom = self.getNextDayDate()

        params.append(str(datetom.month))
        params.append(str(datetom.day))


        year1 = str(datetom.year)[0:2]
        year2 = str(datetom.year)[2:4]
        params.append(year1)
        params.append(year2)

        params.append(str(Conf.WAKEUPHOUR))
        params.append(str(Conf.WAKEUPMINUTE))

        d = self.sendIPMICommand(params)
        return d

    def sendSyncTime(self, value=None):
        logging.debug("sending current time to switch.")

        params = []
        params.append('-H')
        params.append(Switch.IPADDRESS)
        params.append('-U')
        params.append(Switch.USERNAME)
        params.append('-P')
        params.append(Switch.PASSWORD)
        params.append('raw')
        params.append('0x30')
        params.append('0x3c')

        currentTime = self.getCurrentTime()

        params.append(str(currentTime.month))
        params.append(str(currentTime.day))

        year1 = str(currentTime.year)[0:2]
        year2 = str(currentTime.year)[2:4]
        params.append(year1)
        params.append(year2)

        params.append(str(currentTime.hour))
        params.append(str(currentTime.minute))

        d = self.sendIPMICommand(params)
        return d

    #for triggering power cycle
    def sendIPMIAck(self, value=None):
        params = []
        params.append('-H')
        params.append(Switch.IPADDRESS)
        params.append('-U')
        params.append(Switch.USERNAME)
        params.append('-P')
        params.append(Switch.PASSWORD)
        params.append('raw')
        params.append(Switch.POWERONCMD)
        params.append(Switch.ACK)
        params = tuple(params)

        d = self.sendIPMICommand(params)
        return d

    def parseClustat(self, line):
            line = line.split()
            LocalWordIndex = line.index('Local,')
            HostName = line[LocalWordIndex - 3]
            logging.debug("local hostname: %s" % HostName)
            return HostName

    def getVirtualIP(self):
        hostfile = open("/etc/hosts", "r")
        lines = hostfile.readlines()
        ipaddress = ""
        for line in lines:
            if "virtual" in line:
                ipaddress = re.findall("(?:[0-9]{1,3}\.){3}[0-9]{1,3}" , line)[0]
                break

        hostfile.close()
        return ipaddress

    #NodeChecker
    def checkWhichNode(self, value=None):
        logging.debug("checking which node")
        cmd = '/usr/sbin/clustat'
        d = utils.getProcessOutput(cmd)
        d.addCallback(self.parseClustat)
        return d

    def checkIfDisabled(self, line):
        d = None
        if line.find("Success") >= 0:
            logging.debug("successfully disabled")
            d = defer.succeed(None)
        elif line.find("Failed") >= 0:
            #or still proceed with shutdown?
            logging.error("failed to disable for some reason")
            d = defer.succeed(None)
        return d

    #for powering of Mgmt VM
    def shutdownManagementVM(self, value=None):
        logging.debug('disabling Management VM...')
        cmd = '/usr/sbin/clusvcadm'
        params = []
        params.append('-d')
        params.append('vm:a_vm_ldap')

        d = utils.getProcessOutput(cmd, params)
        d.addCallback(self.checkIfDisabled)

        return d

    def shutdownLMS(self, value=None):
        logging.debug('disabling LMS VM...')
        cmd = '/usr/sbin/clusvcadm'
        params = []
        params.append('-d')
        params.append('vm:b_vm_lms')

        d = utils.getProcessOutput(cmd, params)
        d.addCallback(self.checkIfDisabled)

        return d

    def shutdownRDPA(self, value=None):
        logging.debug('disabling RDPA VM...')
        cmd = '/usr/sbin/clusvcadm'
        params = []
        params.append('-d')
        params.append('vm:a_vm_rdpa')

        d = utils.getProcessOutput(cmd, params)
        d.addCallback(self.checkIfDisabled)

        return d

    def shutdownRDPB(self, value=None):
        logging.debug('disabling RDPB VM...')
        cmd = '/usr/sbin/clusvcadm'
        params = []
        params.append('-d')
        params.append('vm:b_vm_rdpb')

        d = utils.getProcessOutput(cmd, params)
        d.addCallback(self.checkIfDisabled)

        return d

    def shutdownNFS(self, value=None):
        logging.debug('disabling NFS...')
        cmd = '/usr/sbin/clusvcadm'
        params = []
        params.append('-d')
        params.append('service:nfs-shared')

        d = utils.getProcessOutput(cmd, params)
        d.addCallback(self.checkIfDisabled)

        return d

    def lockResources(self, value=None):
        logging.debug('locking resources via clusvcadm')
        cmd = '/usr/sbin/clusvcadm'
        params = []
        params.append('-l')

        d = utils.getProcessOutput(cmd, params)
        #if lock fails, procedure should still proceed
        return d
    
    def _powerOff(self, buffer):
        logging.debug("poweroff command executed")
        cmd = '/sbin/poweroff'
        d = utils.getProcessOutput(cmd)
        return d

    def startShutdown(self):
        logging.debug("Attempting to start Shutdown process...")
        returnValue = None
        if NodeA.shuttingDownCancelled == True or NodeB.shuttingDownCancelled == True:
            NodeA.shuttingDownCancelled = False
            NodeB.shuttingDownCancelled = False
            NodeA.serverState = ServerState.ON
            NodeB.serverState = ServerState.ON
            logging.info("Shutdown was cancelled")
            returnValue = None
        elif NodeA.shuttingDownPostponed == True or NodeB.shuttingDownPostponed == True:
            logging.info("Shutdown postponed. Server state set to countdown_in_progress")
            NodeA.shuttingDownPostponed = False
            NodeB.shuttingDownPostponed = False
            NodeA.serverState = ServerState.COUNTDOWN_IN_PROGRESS
            NodeB.serverState = ServerState.COUNTDOWN_IN_PROGRESS
            self.postponeToggle = True
            self.normalShutdown()
        else:
            logging.info("shutdown now proceeding")
            NodeA.serverState = ServerState.SHUTDOWN_IN_PROGRESS
            NodeB.serverState = ServerState.SHUTDOWN_IN_PROGRESS
            cmd = '/sbin/poweroff'
            #Todo: simplify this for Mgmt Vm based operation
            #d = self.powerDownThinClients()
            #d.addCallback(self.sendIPMIAck)
            d = self.sendIPMIAck()
            d.addCallback(self.sendSyncTime)
            #TODO: capture error on ipmi
            d.addCallback(self.sendWakeUpTime)
            d.addCallback(self.lockResources)
            d.addCallback(self.shutdownManagementVM)
            d.addCallback(self.shutdownNFS)
            d.addCallback(self.shutdownLMS)
            d.addCallback(self.shutdownRDPA)
            d.addCallback(self.shutdownRDPB)
            d.addCallback(self.checkWhichNode) 
            d.addCallback(self.shutdownNeighbor)
            d.addCallback(self._powerOff)
            d.addCallback(self._logExitValue)
            returnValue = d
        return returnValue

    def emergencyShutdown(self):
        logging.info("emegergency shutdown!")

        NodeA.serverState = ServerState.SHUTDOWN_IN_PROGRESS
        NodeB.serverState = ServerState.SHUTDOWN_IN_PROGRESS

        #d = self.powerDownThinClients()
        #d.addCallback(self.sendIPMIAck)
        d = self.sendIPMIAck()
        d.addCallback(self.sendSyncTime)
        d.addCallback(self.resetWakeup)
        d.addCallback(self.lockResources)
        d.addCallback(self.shutdownManagementVM)
        d.addCallback(self.shutdownNFS)
        d.addCallback(self.shutdownLMS)
        d.addCallback(self.shutdownRDPA)
        d.addCallback(self.shutdownRDPB)
        d.addCallback(self.checkWhichNode) 
        d.addCallback(self.shutdownNeighbor)
        d.addCallback(self._powerOff)
        d.addCallback(self._logExitValue)

        return d

    def shutdownNeighbor(self, hostname):
        logging.debug("shutting down neighbor  of %s" % hostname)
        node = hostname.split('.')[0]
        schoolID = hostname.split('.')[1]
        cmd = '/usr/bin/ssh'
        params = []
        params.append('-o')
        params.append('StrictHostKeyChecking no')
        if node == 'sa':
            params.append('root@sb.%s.cloudtop.ph' % (schoolID))
        else:
            params.append('root@sa.%s.cloudtop.ph' % (schoolID))
        params.append('"/sbin/poweroff"')
        params = tuple(params)
        d = utils.getProcessOutput(cmd, params)
        d.addCallback(self._logExitValue)
        return d

    def setPowerUpCmd(self, hostname):
        neigbor = None
        nodeA = 'sa'
        nodeB = 'sb'
        if nodeA in hostname:
            neighbor = hostname.replace(nodeA, nodeB)
        else:
            neighbor = hostname.replace(nodeB, nodeA)

        params = []
        params.append('-H')
        params.append(neighbor)
        params.append('-U')
        params.append(NodeB.IPMIUSER)
        params.append('-P')
        params.append(NodeB.IPMIPASS)
        params.append('chassis')
        params.append('power')
        params.append('on')

        return params
    
    def powerUpNeighbor(self):
        d = self.checkWhichNode()
        d.addCallback(self.setPowerUpCmd)
        d.addCallback(self.sendIPMICommand)
        return d

    def shutdownBothBaremetals(self):
        cmd = 'ssh'
        params1 = []
        params2 = []
        params1.append('root@%s' % NodeA.IPADDRESS)
        params2.append('root@%s' % NodeB.IPADDRESS)
        params1.append('\"poweroff\"')
        params2.append('\"poweroff\"')

        d = utils.getProcessOutput(cmd, params1)
        d.addCallback(utils.getProcessOutput, cmd, params2)
        return d

    def normalShutdown(self):
        cmd = ServerNotifs.NORMAL_SHUTDOWN_START_COUNTDOWN | Conf.DEFAULTSCHEDULEDSHUTDOWNWAITTIME

        self.transport.write(RDPMessage.normalShutdownMsg('shutdownSoon', str(self.shutdownDelay))\
                , ThinClient.DEFAULT_ADDR)
        if self.postponeToggle == False:
            logging.debug("no postponement received. Scheduled shutdown will now proceed")
            NodeA.serverState = ServerState.COUNTDOWN_IN_PROGRESS
            NodeB.serverState = ServerState.COUNTDOWN_IN_PROGRESS
            d = task.deferLater(reactor, self.shutdownDelay, self.startShutdown)
        else:
            d = task.deferLater(reactor, self.shutdownDelay, self.normalShutdown)
            self.postponeToggle = False
        # self.schedulePowerUp()
        self.shutdownDelay = Conf.DEFAULTSCHEDULEDSHUTDOWNWAITTIME
        return d

    def schedulePowerUp(self):
        logging.info("Scheduling powerup using IPMI")
        params = []
        params.append('-H')
        params.append(NodeA.IPMIHOST)
        params.append('-U')
        params.append(NodeA.IPMIUSER)
        params.append('-P')
        params.append(NodeA.IPMIPASS)
        params.append('chassis')
        params.append('power')
        params.append('up')
        params = tuple(params)
        

        d = task.deferLater(reactor, self._timeFromPowerUp(), self.sendIPMICommand, params)

    def postponeShutdown(self, delay):
        if Power.state == PowerState.AC:
            logging.info("postpone shutdown request accepted")
            NodeA.shuttingDownPostponed = True
            NodeB.shuttingDownPostponed = True
            self.shutdownDelay = int(delay, 16)
        elif Power.state == PowerState.BATTERYMODE:
            logging.debug("postpone shutdown command not accepted. System is using Battery")

    def cancelShutdown(self):
        NodeA.shuttingDownCancelled = True
        NodeB.shuttingDownCancelled = True

    def executeReducedPowerMode(self):
        NodeB.serverState = ServerState.SHUTDOWN_IN_PROGRESS
        cmd = 'singleservermode'
        location = '/usr/sbin/'
       
        d = utils.getProcessOutput("%s%s" % (location, cmd))
        return d

    def ACRestoredFromHighPower(self):
        Power.state = PowerState.AC

    def ACRestoredFromLowPower(self):
        pass

    def grantShutdownRequest(self):
        pass        

    def processCommand(self, msg):
        #check status of CPU
        logging.debug("processing datagram %s" % msg)
        payload = None
        rdpmsg = None
        if len(msg) > 4:
            logging.debug("datagram received from thinclient with length %d" % len(msg))
          
            command,payload = RDPMessageParser.translateCommand(msg)
            rdpmsg = RDPMessage(msg)
        else:
            logging.debug("datagram received from switch")
            if len(msg) > 1: payload = msg[1:]
            command = msg[0]
        if command == Command.SHUTDOWN_IMMEDIATE:
            if NodeA.serverState == ServerState.ON or NodeB.serverState == ServerState.ON:
                self.sendIPMIAck()
                self.emergencyShutdown()
            elif NodeA.serverState == ServerState.SHUTDOWN_IN_PROGRESS and\
                NodeB.serverState == ServerState.SHUTDOWN_IN_PROGRESS:
                pass
        elif command == Command.REDUCE_POWER:
            if NodeA.serverState == ServerState.ON and NodeB.serverState == ServerState.ON:
                self.executeReducedPowerMode()
            elif NodeB.serverState == ServerState.SHUTDOWN_IN_PROGRESS:
                #need handling here?
                logging.debug("ignoring Single Server Mode request because 1 node is shutting down")
            elif NodeB.serverSate == ServerState.OFF:
                logging.debug("ignoring Single Server Mode request because 1 node is already down")
        elif command == Command.SHUTDOWN_CANCEL:
            if NodeA.serverState == ServerState.COUNTDOWN_IN_PROGRESS and\
                NodeB.serverState == ServerState.COUNTDOWN_IN_PROGRESS:
                self.cancelShutdown()
        elif command == Command.AC_RESTORED:
            if NodeA.serverState == ServerState.SHUTDOWN_IN_PROGRESS and\
                NodeB.serverState == ServerState.SHUTDOWN_IN_PROGRESS:
                #can't do anything anymore
                pass
            elif Power.state == PowerState.BATTERYMODE:
                #nothing to do
                pass
            elif Power.state == PowerState.LOWBATTERY:
                self.ACRestoredFromLowPower()
        elif command == Command.POSTPONE:
            if NodeA.serverState == ServerState.COUNTDOWN_IN_PROGRESS and\
                NodeB.serverState ==ServerState.COUNTDOWN_IN_PROGRESS:
                self.postponeShutdown(payload)
        elif command == Command.UPDATE:
            self.updateTCDatabase()
        elif command == Command.SHUTDOWN_REQUEST:
            if NodeA.serverState == ServerState.COUNTDOWN_IN_PROGRESS:
                pass
            if NodeB.serverState == ServerState.COUNTDOWN_IN_PROGRESS:
                pass
            else:
                self.grantShutdownRequest() 
        elif command == Command.SHUTDOWN_NORMAL:
            if NodeA.serverState == ServerState.COUNTDOWN_IN_PROGRESS:
                logging.debug("shutdown already progressing. ignoring requests")
                pass
            if NodeB.serverState == ServerState.COUNTDOWN_IN_PROGRESS:
                logging.debug("shutdown already progressing. ignoring requests")
                pass
            else:
                logging.debug("deprecated normal shutdown requested. ignoring")
        elif command == Command.POENOTIF:
            logging.debug("PoE notif from switch received")
            self.evaluatePoENotif(payload)
        elif command == Command.RDPREQUEST:
            logging.debug("notification from RDP received")
            self.sendAckToRDP(rdpmsg)
            self.evaluateRDPRequest(payload)
        elif command == Command.KEEPALIVE:
            self.transport.write(command, (Switch.IPADDRESS, 8880))
            logging.debug('replying to switch Checkalive packet')
        elif command == Command.SWITCHREADY:
            self.thinClientsInitialized = False
            self.readyPorts = ord(payload)
            logging.debug('switch sents ready ports on startup')
        elif command == Command.RDPSESSIONPOWER:
            logging.debug('Request from RDP/Epoptes for power control of a TC')
            self.controlRDPSessionPower(payload)

    #the scenario assumes that the port number matches the PoECounter
    #if not matching, I'm not sure of the next action
    #need to add functionality if UDP notif doesn't arrive
    def evaluatePoENotif(self, payload):
        logging.debug("evaluating PoE Notification from switch with length %d" % len(payload))
        ret = None
        port = ord(payload[0])

        if Conf.TESTMODE:
            #3 TCs to be initialized only on testmode
            #hardcoded for now
            #what if more than 16?!
            if self.PoECounter >= 3:
                self.thinClientsInitialized = True

        if self.PoECounter >= Conf.MAXCLIENTS:
            logging.debug("ThinClient map initialization has ended")
            self.thinClientsInitialized = True

        if payload[1] == '\x01': #true
            d1 = None   
            if self.thinClientsInitialized:
                d1 = self.powerUpPoE(port)
            d2 = task.deferLater(reactor, 5, self.powerUpPoE, port+1)
            #errback here needed
            #d3 should be callback for d2
            d3 = task.deferLater(reactor, 1, Mapper.addNewThinClient, port)
            d3.addCallback(self.sendNotificationToRDP,'TCAdded')
            if not self.thinClientsInitialized:
                self.PoECounter = self.PoECounter + 1
            ret = d1
        elif payload[1] == '\x00':
            d = Mapper.removeThinClient(port)
            d.addCallback(self.sendNotificationToRDP,'TCRemoved')
            if self.thinClientsInitialized == False:
                self.PoECounter = self.PoECounter + 1
            ret = d
        else:
            logging.debug("PoE on port %d failed. LAN cable probably disconnected" % port)
            self.PoECounter = self.PoECounter + 1
            
    def evaluateRDPRequest(self, payload):
        tcport = ord(payload[0])
        requestedState = ord(payload[1])

        if requestedState == 0:
            d = task.deferLater(reactor, 10, self.powerDownPoE, tcport)
            d.addCallback(Mapper.removeThinClient, tcport)
        elif requestedState == 1:
            d = self.powerUpPoE(tcport)
            d.addCallback(task.deferLater, reactor, 10, Mapper.addNewThinClient, tcport)

    def sendNotificationToRDP(self, info):
        msg = RDPMessage.updateMessage(info)
        self.transport.write(msg, ThinClient.DEFAULT_ADDR)

    #TODO: remove 
    def initializeThinClient(self):
        logging.debug("initializing an active ThinClient")
        self.PoECounter = self.PoECounter +1
        self.waitingForPoEConfirm = True

        Mapper.addNewThinClient()
        
        timer.sleep(3) # 3-second grace period before trying to activate the next PoE   
        d = self.powerUpPoE(self.PoECounter)

        return d

    def startProtocol(self):
        logging.info("Power Daemon has now started")
        self.address = ThinClient.DEFAULT_ADDR
        if Conf.SCHEDULESHUTDOWN:
            logging.debug("Scheduling shutdown based on config")
            d = task.deferLater(reactor, self._timeFromShutdown(), self.normalShutdown)
        else:
            logging.debug("Daily shutdown schedule disabled")
        #power up port 0
        d2 = task.deferLater(reactor, 15, self.powerUpPoE, 0)

        #slightly hack, time is arbitrary
        #d3 = task.deferLater(reactor, 20, self.sendSyncTime)

    #to be updated to a initialize() method
    def powerUpThinClients(self):
        logging.debug("sending IPMI command to power up ThinClients via Switch")
        params = []
        params.append('-H')
        params.append(Switch.IPADDRESS)
        params.append('-U')
        params.append(Switch.USERNAME)
        params.append('-P')
        params.append(Switch.PASSWORD)
        params.append('raw')
        params.append(Switch.TCPOWERCMD1)
        params.append(Switch.TCPOWERCMD2)
        params.append(hex(0))
        params.append(Switch.ON)
        d = self.sendIPMICommand(params)
        d.addCallback(self._logExitValue)
        for tcnum in range(1, 15):
            params = []
            params.append('-H')
            params.append(Switch.IPADDRESS)
            params.append('-U')
            params.append(Switch.USERNAME)
            params.append('-P')
            params.append(Switch.PASSWORD)
            params.append('raw')
            params.append(Switch.TCPOWERCMD1)
            params.append(Switch.TCPOWERCMD2)
            params.append(hex(tcnum))
            params.append(Switch.ON)

            timer.sleep(2)
            d.addCallback(self.sendIPMICommand,params)
            d.addCallback(self._logExitValue)
        return d

    def powerUpPoE(self, num):
        logging.debug("sending power to PoE port %d" % num)

        params = []
        params.append('-H')
        params.append(Switch.IPADDRESS)
        params.append('-U')
        params.append(Switch.USERNAME)
        params.append('-P')
        params.append(Switch.PASSWORD)
        params.append('raw')
        params.append(Switch.TCPOWERCMD1)
        params.append(Switch.TCPOWERCMD2)
        params.append(hex(num))
        params.append(Switch.ON)    

        d = self.sendIPMICommand(params)  
        return d  

    def powerDownPoE(self, port):
        logging.info("removing power to PoE port %d" % port)

        params = []
        params.append('-H')
        params.append(Switch.IPADDRESS)
        params.append('-U')
        params.append(Switch.USERNAME)
        params.append('-P')
        params.append(Switch.PASSWORD)
        params.append('raw')
        params.append(Switch.TCPOWERCMD1)
        params.append(Switch.TCPOWERCMD2)
        params.append(hex(port))
        params.append(Switch.OFF)    

        d = self.sendIPMICommand(params)
        return d

    def powerDownThinClients(self):
        logging.debug("preparing IPMI command for thinclient powerdown via switch")
        params = []
        params.append('-H')
        params.append(Switch.IPADDRESS)
        params.append('-U')
        params.append(Switch.USERNAME)
        params.append('-P')
        params.append(Switch.PASSWORD)
        params.append('raw')
        params.append(Switch.TCALLPOWER1)
        params.append(Switch.TCALLPOWER2)
        params.append(Switch.OFF)

        d = self.sendIPMICommand(params)
        d.addCallback(self._logExitValue)
        return d

    def getNextDayDate(self):
        if Conf.TESTMODE == False:
            oneDay = timedelta(days=1)
            targetday = date.today() + oneDay
        else:
            targetday = date.today()
        return date(targetday.year, targetday.month, targetday.day)

    def _timeFromPowerUp(self):
        currentTime = datetime.now()
        oneDay = timedelta(days=1)
        tomorrow = date.today() + oneDay
        shutdownTime = datetime.combine(tomorrow, time(Conf.WAKEUPHOUR,Conf.WAKEUPMINUTE))
        timeDiff = shutdownTime - currentTime
        return timeDiff.seconds

    def _timeFromShutdown(self):
        #wont work after 6pm (negative time!)
        currentTime = datetime.now()
        shutdownTime = datetime.combine(date.today(), time(Conf.SHUTDOWNHOUR,Conf.SHUTDOWNMINUTE))    
        timeDiff = shutdownTime - currentTime
        return timeDiff.seconds

    def datagramReceived(self, data, (host, port)):
        self.address = (host, port)
        logging.info("datagram received with length %d" % len(data))
        self.processCommand(data)      

    def updateTCDatabase(self):
        
        IPAddressFinder.update()

    def powerOffThinClient(self):
        pass
        

#power manager factory class
class PowerManagerFactory(protocol.ServerFactory):
    protocol = None
    #instantiates a power Manager class on 
    def buildProtocol(self, addr):
        self.protocol = PowerManager()
        return self.protocol

def SIGTERMHandler():
    logging.debug('Power manager received SIGTERM. Exiting...')
    reactor.stop()
    exit()

#main function
#transfer to executable?
if __name__ == "__main__":
    signal.signal(signal.SIGTERM, SIGTERMHandler)
    fillAllDefaults("/etc/power_mgmt.cfg")
    FORMAT = '%(asctime)-15s %(message)s'
    logging.basicConfig(filename=Conf.LOGFILE,level=Conf.LOGLEVEL, format=FORMAT)
    DBHandler.openDB(Conf.MAPFILE)
    #run reactor
    powerManager = PowerManager()
    virtualIP = powerManager.getVirtualIP()
    reactor.listenUDP(8880, powerManager)
    reactor.run()
