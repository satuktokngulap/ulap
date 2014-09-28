import logging, socket

#Power Conf class
class Conf():
    LOGFILE = '/var/log/PowerManagerDeamon.log'
    MAPFILE = ''
    LOGLEVEL = logging.DEBUG
    SCHEDULESHUTDOWN = False
    TESTMODE = False
    SHUTDOWNHOUR = 20
    SHUTDOWNMINUTE = 0
    WAKEUPHOUR = 5
    WAKEUPMINUTE = 0
    MAXCLIENTS = 16 
    DEFAULTSCHEDULEDSHUTDOWNWAITTIME = 0x258

#States
class ServerState():
    COUNTDOWN_IN_PROGRESS = 'countdown_in_progress'
    SHUTDOWN_IN_PROGRESS = 'shutdown_in_progress'
    SHUTDOWN_CANCEL = 'shutdown_cancelled'
    #waiting constant redundant with Countdown_in_progress (?)
    WAITING = 'waiting'
    ON = 'on'
    ONE_NODE_ONLY = '1-node only'

class PowerState():
    AC = '0x01'
    BATTERYMODE = '0x02'
    LOWBATTERY = '0x03'
    CRITICALBATTERY = '0x04'

class SwitchState():
    STARTUP = True

class Power():
    state = PowerState.AC

class MasterTC():
    ID ='2'

class Switch():
    ID = 0x300000
    IPADDRESS = '10.18.221.210'
    USERNAME = 'Admin'
    PASSWORD =  'Admin'
    #comment this out first
    OEMCMD = '0xC0'
    POWERONCMD = '0x30'
    ACK = '0x33'
    ON = '0x1'
    OFF = '0x0'
    TCPOWERCMD1 = '0x32'
    TCPOWERCMD2 = '0x38'
    TCALLPOWER1 = '0x32'
    TCALLPOWER2 = '0x31'
    
class NodeA():
    #upNodeCount = 2
    serverState = ServerState.ON
    shuttingDownCancelled = False
    shuttingDownPostponed = False
    IPADDRESS = '10.18.221.11'
    IPMIHOST = '10.18.221.111'
    IPMIUSER = 'ADMIN'
    IPMIPASS = 'admin@123'

class NodeB():
    serverState = ServerState.ON
    shuttingDownCancelled = False
    shuttingDownPostponed = False
    IPADDRESS = '10.18.221.12'
    IPMIHOST = '10.18.221.112'
    IPMIUSER = 'ADMIN'
    IPMIPASS = 'admin@123'

class MgmtVM():
    IPADDRESS = '10.18.221.21'
    

#refactored to be a instantiated
class ThinClient():
    #class variables
    DEFAULT_ADDR = ('172.16.1.5', 8880)
    SERVERA_ADDR = ('172.16.1.5', 8880)
    SERVERB_ADDR = ('172.16.1.6', 8880)
    ThinClientInitialized = False

    def __init__(self, IDtouple=None, portNum=None, sessionID=None, userID=None):
        if IDtouple is not None:
            #assumes correct input
            self.setIPAddress(IDtouple[0])
            self.setMacAddress(IDtouple[1])
            self.setSwitchPoEPort(portNum)

            #default
            self.setSessionID(sessionID)

    def getIPAddress(self):
        return self.ipAddress

    def setIPAddress(self, IP):
        self.ipAddress = IP

    def getMacAddress(self):
        return self.macAddress

    #mac address is unique for ThinClient
    def setMacAddress(self, Mac):
        self.macAddress = Mac

    def setSessionID(self, Id):
        self.sessionID = Id

    def getSessionID(self):
        return self.sessionID

    def setUserID(self, Id):
        self.userID = Id

    def getUserID(self):
        return self.userID

    def setSwitchPoEPort(self, Port):
        self.port = Port

    def getSwitchPoEPort(self):
        return self.port

class Session():

    def __init__(self, sessionID=None, userID=None):
        if sessionID is not None:
            self.sessionID = sessionID
        if userID is not None:
            self.userID = userID

    def setUserID(self, Id):
        self.userID = Id

    def getUserID(self):
        return self.userID

    def setSessionID(self, Id):
        self.sessionID = Id

    def getSessionID(self):
        return self.sessionID

