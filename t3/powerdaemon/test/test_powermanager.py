#Power Manager Unit Test
from mock import Mock, call, patch
from twisted.internet import defer, reactor
from twisted.trial import unittest

from PowerManager import PowerManagerFactory, PowerManager
from powermodels import NodeA, NodeB, ServerState, Switch, Conf, ThinClient, MasterTC
from PowerManager import PowerState, Power
from PowerManager import IPMISecurity
from PowerManager import ServerNotifs, Command

from Crypto.Cipher import AES
from datetime import datetime, date, time, timedelta

#PowerManager Testsuite
class PowerManagerTestSuite(unittest.TestCase):
    def setUp(self):
        self.powerManager = PowerManager()
        self.postponeToggle = False

    def tearDown(self):
        NodeA.serverState = ServerState.ON
        NodeA.shuttingDownCancelled = False
        NodeA.shuttingDownPostponed = False
        NodeB.serverState = ServerState.ON
        NodeB.shuttingDownCancelled = False
        NodeB.shuttingDownPostponed = False
        Conf.SCHEDULESHUTDOWN = True
        Conf.TESTMODE = True
        self.powerManager.shutdownDelay = None
        Power.state = PowerState.AC
        self.waitingForPoEConfirm = False
        self.powerManager.thinClientsInitialized = False

    @patch('PowerManager.utils')
    def testCheckWhichNode(self, utils):
        cmd = '/usr/sbin/clustat'
        value = None
        utils.getProcessOutput = Mock()
        utils.getProcessOutput.addCallback = Mock(return_value=2)
        parseClustat = Mock()
        self.powerManager.parseClustat = parseClustat

        ret = self.powerManager.checkWhichNode(value)

        utils.getProcessOutput().addCallback.assert_called_with(parseClustat)

    def testParseClustat(self):
        line = "sb.105134.cloudtop.ph                       2 Online, Local, rgmanager"

        ret  = self.powerManager.parseClustat(line)

        self.assertEqual(ret, 'sb.105134.cloudtop.ph')

    def testDatagramReceived(self):
        data = '\x05\x01'
        host = '10.225.3.31'
        port = 8888
        self.powerManager.processCommand = Mock()

        self.powerManager.datagramReceived(data, (host,port))

        self.powerManager.processCommand.assert_called_with(data)
  
    def testProcessCommand_ShutdownFromOn(self):
        self.powerManager.sendIPMIAck = Mock()
        cmd = '\x05'
        self.powerManager.startShutdown = Mock()
        NodeA.serverState = ServerState.ON
        NodeB.serverState = ServerState.ON

        self.powerManager.processCommand(cmd)

        assert self.powerManager.startShutdown.called

    testProcessCommand_ShutdownFromOn.skip ='deprecated'

    def testProcessCommand_ReducedPowerMode(self):
        cmd = Command.REDUCE_POWER
        self.powerManager.executeReducedPowerMode = Mock()
        NodeA.serverState = ServerState.ON
        NodeB.serverState = ServerState.ON

        self.powerManager.processCommand(cmd)

        assert self.powerManager.executeReducedPowerMode.called

    @patch('PowerManager.utils')
    def testStartShutdown(self, utils):
        #Poweroff BOTH nodes
        utils.getProcessOutput = Mock()
        self.powerManager.powerDownThinClients = Mock()
        self.powerManager.checkWhichNode = Mock()
        self.powerManager.checkWhichNode.addCallback = Mock()
        self.powerManager.shutdownNeighbor = Mock()
        self.powerManager._logExitValue = Mock()
        self.powerManager.sendIPMIAck = Mock()
        self.powerManager.sendSyncTime = Mock()
        self.powerManager.sendWakeUpTime = Mock()
        self.powerManager.shutdownManagementVM = Mock()
        self.powerManager.shutdownNFS = Mock()
        self.powerManager.lockResources = Mock()
        self.powerManager.shutdownLMS = Mock()
        self.powerManager.shutdownRDPA = Mock()
        self.powerManager.shutdownRDPB = Mock()
        self.powerManager._powerOff = Mock()

        d = self.powerManager.startShutdown()

        self.assertEqual(NodeA.serverState, ServerState.SHUTDOWN_IN_PROGRESS)
        self.assertEqual(NodeB.serverState, ServerState.SHUTDOWN_IN_PROGRESS)
        assert self.powerManager.sendIPMIAck.called
        # self.assertEqual(self.powerManager.sendIPMIAck().addCallback.call_args_list[0],call(self.powerManager.sendIPMIAck))
        self.assertEqual(self.powerManager.sendIPMIAck().addCallback.call_args_list[0],call(self.powerManager.sendSyncTime))
        self.assertEqual(self.powerManager.sendIPMIAck().addCallback.call_args_list[1],call(self.powerManager.sendWakeUpTime))
        self.assertEqual(self.powerManager.sendIPMIAck().addCallback.call_args_list[2],call(self.powerManager.lockResources))
        self.assertEqual(self.powerManager.sendIPMIAck().addCallback.call_args_list[3],call(self.powerManager.shutdownManagementVM))
        self.assertEqual(self.powerManager.sendIPMIAck().addCallback.call_args_list[4],call(self.powerManager.shutdownNFS))
        self.assertEqual(self.powerManager.sendIPMIAck().addCallback.call_args_list[5],call(self.powerManager.shutdownLMS))
        self.assertEqual(self.powerManager.sendIPMIAck().addCallback.call_args_list[6],call(self.powerManager.shutdownRDPA))
        self.assertEqual(self.powerManager.sendIPMIAck().addCallback.call_args_list[7],call(self.powerManager.shutdownRDPB))
        self.assertEqual(self.powerManager.sendIPMIAck().addCallback.call_args_list[8],call(self.powerManager.checkWhichNode))
        self.assertEqual(self.powerManager.sendIPMIAck().addCallback.call_args_list[9],call(self.powerManager.shutdownNeighbor))
        self.assertEqual(self.powerManager.sendIPMIAck().addCallback.call_args_list[10],call(self.powerManager._powerOff))


    def testEmergencyShutdown(self):
        self.powerManager.powerDownThinClients = Mock()
        self.powerManager.checkWhichNode = Mock()
        self.powerManager.shutdownNeighbor = Mock()
        self.powerManager._logExitValue = Mock()
        self.powerManager.sendIPMIAck = Mock()
        self.powerManager.shutdownManagementVM = Mock()
        self.powerManager.shutdownNFS = Mock()
        self.powerManager.lockResources = Mock()
        self.powerManager.shutdownLMS = Mock()
        self.powerManager.shutdownRDPA = Mock()
        self.powerManager.shutdownRDPB = Mock()
        self.powerManager.sendSyncTime = Mock()
        self.powerManager.resetWakeup = Mock()
        self.powerManager._powerOff = Mock()


        d = self.powerManager.emergencyShutdown()

        # assert self.powerManager.powerDownThinClients.called
        assert self.powerManager.sendIPMIAck.called
        # self.assertEqual(self.powerManager.powerDownThinClients().addCallback.call_args_list[0],call(self.powerManager.sendIPMIAck))
        self.assertEqual(self.powerManager.sendIPMIAck().addCallback.call_args_list[0],call(self.powerManager.sendSyncTime))
        self.assertEqual(self.powerManager.sendIPMIAck().addCallback.call_args_list[1],call(self.powerManager.resetWakeup))
        self.assertEqual(self.powerManager.sendIPMIAck().addCallback.call_args_list[2],call(self.powerManager.lockResources))
        self.assertEqual(self.powerManager.sendIPMIAck().addCallback.call_args_list[3],call(self.powerManager.shutdownManagementVM))
        self.assertEqual(self.powerManager.sendIPMIAck().addCallback.call_args_list[4],call(self.powerManager.shutdownNFS))
        self.assertEqual(self.powerManager.sendIPMIAck().addCallback.call_args_list[5],call(self.powerManager.shutdownLMS))
        self.assertEqual(self.powerManager.sendIPMIAck().addCallback.call_args_list[6],call(self.powerManager.shutdownRDPA))
        self.assertEqual(self.powerManager.sendIPMIAck().addCallback.call_args_list[7],call(self.powerManager.shutdownRDPB))
        self.assertEqual(self.powerManager.sendIPMIAck().addCallback.call_args_list[8],call(self.powerManager.checkWhichNode))
        self.assertEqual(self.powerManager.sendIPMIAck().addCallback.call_args_list[9],call(self.powerManager.shutdownNeighbor))
        self.assertEqual(self.powerManager.sendIPMIAck().addCallback.call_args_list[10],call(self.powerManager._powerOff))

    def testResetWakeup(self):
        self.powerManager.sendIPMICommand = Mock(return_value=defer.succeed(None))
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

        d = self.powerManager.resetWakeup()

        self.powerManager.sendIPMICommand.assert_called_with(params)

    #TODO
    def testSendSyncTime(self):
        pass

    def testSendWakeupTime(self):
        pass

    #testing with actual date and time objects
    def testGetNexDayDate(self):
        Conf.TESTMODE = False
        delta = timedelta(days=1)
        tomorrow = date.today() + delta
        testdate = date(tomorrow.year, tomorrow.month, tomorrow.day)

        ret = self.powerManager.getNextDayDate()

        self.assertEqual(ret, testdate)

    #testing with actual date and time objects
    def testGetNextDayDate_testmode(self):
        today = date.today()
        testdate = date(today.year, today.month, today.day)

        ret = self.powerManager.getNextDayDate()

        self.assertEqual(ret, testdate)


    @patch('PowerManager.utils')
    def test_powerOff(self, utils):
        value = None
        cmd = '/sbin/poweroff'

        d = self.powerManager._powerOff(value)

        utils.getProcessOutput.assert_called_with(cmd)

    @patch('PowerManager.utils')
    def testShutdownNeighbor(self, utils):
        cmd = '/usr/bin/ssh'
        params = []
        params.append('-o')
        params.append('StrictHostKeyChecking no')
        params.append('root@sa.123456.cloudtop.ph')
        params.append('"/sbin/poweroff"')
        params = tuple(params)
        hostname = 'sb.123456.cloudtop.ph'

        self.powerManager.shutdownNeighbor(hostname)

        utils.getProcessOutput.assert_called_with(cmd, params)

    @patch('PowerManager.utils')
    def testShutdownLMS(self, utils):
        cmd = '/usr/sbin/clusvcadm'
        params = []
        params.append('-d')
        params.append('vm:b_vm_lms')
        utils.getProcessOutput = Mock(return_value=defer.succeed(None))
        self.powerManager.checkIfDisabled = Mock()

        d = self.powerManager.shutdownLMS()

        utils.getProcessOutput.assert_called_with(cmd, params)
        #d.addCallback(self.assertEqual, None)

    @patch('PowerManager.utils')
    def testShutdownRDPA(self, utils):
        cmd = '/usr/sbin/clusvcadm'
        params = []
        params.append('-d')
        params.append('vm:a_vm_rdpa')
        utils.getProcessOutput = Mock(return_value=defer.succeed(None))
        self.powerManager.checkIfDisabled = Mock(return_value=defer.succeed(None))

        d = self.powerManager.shutdownRDPA()

        utils.getProcessOutput.assert_called_with(cmd, params)
        d.addCallback(self.assertEqual, None)

    @patch('PowerManager.utils')
    def testShutdownRDPB(self, utils):
        cmd = '/usr/sbin/clusvcadm'
        params = []
        params.append('-d')
        params.append('vm:b_vm_rdpb')
        utils.getProcessOutput = Mock(return_value=defer.succeed(None))
        self.powerManager.checkIfDisabled = Mock(return_value=defer.succeed(None))

        d = self.powerManager.shutdownRDPB()

        utils.getProcessOutput.assert_called_with(cmd, params)
        d.addCallback(self.assertEqual, None)

    @patch('PowerManager.utils')
    def testExecuteReducedPowerMode(self, utils):
        cmd = 'singleservermode'
        directory = '/usr/sbin/'

        d = self.powerManager.executeReducedPowerMode()

        self.assertEqual(NodeB.serverState, ServerState.SHUTDOWN_IN_PROGRESS)
        utils.getProcessOutput.assert_called_with("%s%s" % (directory, cmd))
        d.addCallback(self.assertEqual, None)

    def testSetPowerUpCmd(self):
        hostname = 'sb.105134.cloudtop.ph'
        self.powerManager.sendIPMICommand = Mock(return_value=defer.succeed(None))

        cmd = 'ipmitool'
        params = []
        params.append('-H')
        params.append('sa.105134.cloudtop.ph')
        params.append('-U')
        params.append(NodeB.IPMIUSER)
        params.append('-P')
        params.append(NodeB.IPMIPASS)
        params.append('chassis')
        params.append('power')
        params.append('on')
    
        actualparams = self.powerManager.setPowerUpCmd(hostname)

        self.assertEqual(params, actualparams)

    def testPowerUpNeighbor(self):
        self.powerManager.checkWhichNode = Mock(return_value=defer.succeed(None))
        self.powerManager.setPowerUpCmd = Mock()
        self.powerManager.sendIPMICommand = Mock(return_value=defer.succeed(None))

        self.powerManager.powerUpNeighbor()

        assert self.powerManager.sendIPMICommand.called

    def testSendPowerONStatusToSwitch(self):
        self.powerManager.sendIPMICommand = Mock(return_value=defer.succeed(None))
        #-l for impi over lan
        params =[]
        params.append('-H')
        params.append(Switch.IPADDRESS)
        params.append('-U')
        params.append(Switch.USERNAME)
        params.append('-P')
        params.append(Switch.PASSWORD)
        params.append('raw')
        params.append('0xC0')
        params.append('0x30')
        params = tuple(params)

        d = self.powerManager.sendPowerONStatusToSwitch()

        self.powerManager.sendIPMICommand.assert_called_with(params)
        d.addCallback(self.assertEqual, None)

    def testSendIPMIAck(self):
        self.powerManager.sendIPMICommand = Mock(return_value=defer.succeed(None))
        #-l for impi over lan
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

        d = self.powerManager.sendIPMIAck()

        self.powerManager.sendIPMICommand.assert_called_with(params)
        d.addCallback(self.assertEqual, None)

    @patch('PowerManager.utils')
    def testSendIPMICommand(self, utils):
        cmd = '/usr/bin/ipmitool'
        params = []
        params.append('-H')
        params.append(Switch.IPADDRESS)
        params.append('-U')
        params.append(Switch.USERNAME)
        params.append('-P')
        params.append(Switch.PASSWORD)
        params.append('-a')
        params.append('raw')
        params = tuple(params)


        d = self.powerManager.sendIPMICommand(None, params)

        utils.getProcessOutput.assert_called_with(cmd, params)
        d.addCallback(self.assertEqual, None)

    def testSendPowerOffSwitchPort(self):
        portnum = '0x1'
        self.powerManager.sendIPMICommand = Mock(return_value=\
                defer.succeed(None))
        params = ['-H', Switch.IPADDRESS, '-U', Switch.USERNAME\
            , '-P', Switch.PASSWORD, 'raw', '0x32', '0x38'\
                , portnum, '0x0']

        d = self.powerManager.sendPowerOffSwitchPort(portnum)

        self.powerManager.sendIPMICommand.assert_called_with(params)
        d.addCallback(self.assertEqual, None)

    @patch('PowerManager.ConfigParser.ConfigParser')
    def testGetPortNumberFromMac(self, parser):
        parser.read = Mock()
        parser().get = Mock(side_effect=['94-00-F4-35-FE-94'\
            ,'94-00-F4-35-FE-95'\
            ,'94-00-F4-35-FE-9D'])
        mac = '94-00-F4-35-FE-9D'
        port = '0x2'

        portfromconfig = self.powerManager.getPortNumberFromMac(mac)

        self.assertEqual(port, portfromconfig)

    testGetPortNumberFromMac.skip = "unused or deprecated"

    @patch('PowerManager.Mapper')
    @patch('PowerManager.timer') #mock to avoid actual sleep on test
    def testInitializeThinClient(self, mocktimer, mapper):
        #reads UDP port number. stops at 16
        #send Power to target PoE
        #waits for UDP acknowledgement from Switch (use status?)
        self.powerManager.powerUpPoE = Mock()
        waitingForUDPAck = True
        mockCounter = 2
        self.powerManager.PoECounter = 1

        d = self.powerManager.initializeThinClient()

        self.powerManager.powerUpPoE.assert_called_with(mockCounter)
        self.assertEqual(waitingForUDPAck,self.powerManager.waitingForPoEConfirm)
        assert mapper.addNewThinClient.called

    @patch('PowerManager.task')
    def testStartProtocol(self, task):
        self.powerManager.sendPowerONStatusToSwitch =  Mock()
        self.powerManager.normalShutdown = Mock()
        self.powerManager._timeFromShutdown = Mock()
        self.powerManager.powerUpThinClients = Mock()
        self.powerManager.powerUpThinClients = Mock()
        self.powerManager.sendSyncTime = Mock()

        self.powerManager.startProtocol()

        task.deferLater.assert_has_call(reactor, self.powerManager._timeFromShutdown(), self.powerManager.normalShutdown)
        task.deferLater.assert_has_call(reactor, 15, self.powerManager.powerUpThinClients)
        task.deferLater.assert_has_call(reactor, 20, self.powerManager.powerUpThinClients)
        #assert self.powerManager.sendPowerONStatusToSwitch.called


    @patch('PowerManager.datetime')
    @patch('PowerManager.date')
    def test_getTimeFromShutdown(self, Date, dateTime):
        seconds = 48598
        dateTime.combine = datetime.combine
        dateTime.now = Mock(return_value=\
            datetime(2013,7, 11, 6, 30, 2, 0))
        Date.today = Mock(return_value=date(2013,7,11))

        timediff = self.powerManager._timeFromShutdown()

        self.assertEqual(seconds, timediff)

    @patch('PowerManager.datetime')
    @patch('PowerManager.date')
    def test_getTimeFromPowerUP(self, Date, DateTime):
        seconds = 37798
        DateTime.combine = datetime.combine
        Date.today = Mock(return_value=date(2013,7,11))
        DateTime.now = Mock(return_value=\
            datetime(2013,7, 11, 18, 30, 2, 0))

        timediff = self.powerManager._timeFromPowerUp()

        self.assertEqual(seconds, timediff)

    @patch('PowerManager.task')
    def testNormalShutdown(self, task):
        #defers shutdown task for 10 minutes
        self.powerManager.postponeToggle = False
        self.powerManager.address = ('172.16.1.255', 8880)
        self.powerManager.startShutdown = Mock()
        self.powerManager.transport = Mock()
        self.powerManager.transport.write = Mock()
        self.powerManager.schedulePowerUp = Mock()
        self.powerManager.shutdownDelay = 300
        write = self.powerManager.transport.write

        cmd = ServerNotifs.NORMAL_SHUTDOWN_START_COUNTDOWN | Conf.DEFAULTSCHEDULEDSHUTDOWNWAITTIME

        self.powerManager.normalShutdown()
        
        self.assertEqual(NodeA.serverState, ServerState.COUNTDOWN_IN_PROGRESS)
        self.assertEqual(NodeB.serverState, ServerState.COUNTDOWN_IN_PROGRESS)
        self.assertEqual(self.powerManager.shutdownDelay, Conf.DEFAULTSCHEDULEDSHUTDOWNWAITTIME)
        task.deferLater.assert_called_with(reactor, 300, self.powerManager.startShutdown)
        write.assert_called_with(hex(cmd), (ThinClient.DEFAULT_ADDR[0], ThinClient.DEFAULT_ADDR[1]))

    @patch('PowerManager.task')
    def testNormalShutdown_Postponed(self, task):
        self.powerManager.transport = Mock()
        self.powerManager.transport.write = Mock()
        self.powerManager.schedulePowerUp = Mock()
        self.powerManager.postponeToggle = True

        self.powerManager.normalShutdown()

        task.deferLater.assert_called_with(reactor, self.powerManager.shutdownDelay, self.powerManager.normalShutdown)
        self.assertEqual(self.powerManager.postponeToggle, False)

    @patch('PowerManager.task')
    def testSchedulePowerUp(self, task):
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
        self.powerManager._timeFromPowerUp = Mock(return_value=3600)

        self.powerManager.schedulePowerUp()

        task.deferLater.assert_called_with(reactor, 3600, self.powerManager.sendIPMICommand, params)

    def testReceivedEmergencyShutdown(self):
        command = Command.SHUTDOWN_IMMEDIATE
        self.powerManager.emergencyShutdown = Mock()
        self.powerManager.sendIPMIAck = Mock()
        NodeA.serverstate = ServerState.ON
        NodeB.serverstate = ServerState.ON

        self.powerManager.processCommand(command)

        assert self.powerManager.sendIPMIAck.called
        assert self.powerManager.emergencyShutdown.called

    def testReceivedShutdownCancelCommand(self):
        cmd = Command.SHUTDOWN_CANCEL
        NodeA.serverState = ServerState.COUNTDOWN_IN_PROGRESS
        NodeB.serverState = ServerState.COUNTDOWN_IN_PROGRESS
        self.powerManager.cancelShutdown = Mock()

        self.powerManager.processCommand(cmd)

        assert self.powerManager.cancelShutdown.called

    def testReceivedPostponeCommand(self):
        cmd = Command.POSTPONE
        src = MasterTC.ID
        time = '11111'
        udpMessage = '0x%s%s%s' % (cmd, src, time)  
        NodeA.serverState = ServerState.COUNTDOWN_IN_PROGRESS
        NodeB.serverState = ServerState.COUNTDOWN_IN_PROGRESS
        self.powerManager.postponeShutdown = Mock()

        self.powerManager.processCommand(udpMessage)

        self.powerManager.postponeShutdown.assert_called_with(time)

    def testReceivedPoEUpNotification(self):
        self.powerManager.evaluatePoENotif = Mock()

        cmd = []
        cmd.append(Command.POENOTIF) #command, duh
        cmd.append('\x0B') #portnumber
        cmd.append('\x01') #enabled/disabled
        payload = ['\x0B','\x01']
        
        self.powerManager.processCommand(cmd)

        self.powerManager.evaluatePoENotif.assert_called_with(payload)

    @patch('PowerManager.task')
    @patch('PowerManager.Mapper')
    def testEvaluatePoENotif_PoEConnectionExists(self, mapper, task):
        payload = ['\x07','\x01']
        portnum = 7
        self.powerManager.PoECounter = 2
        self.powerManager.powerUpPoE = Mock()

        ret = self.powerManager.evaluatePoENotif(payload)

        task.deferLater.assert_called_with(reactor, 25, mapper.addNewThinClient,portnum)
        self.assertEqual(3, self.powerManager.PoECounter)

    @patch('PowerManager.Mapper')
    def testEvaluatePoENotif_PoEDisconnected(self, mapper):
        self.powerManager.thinClientsInitialized = True
        payload = ['\x07', '\x00']
        portnumber = 7
        self.powerManager.PoECounter = 2

        ret = self.powerManager.evaluatePoENotif(payload)

        mapper.removeThinClient.assert_called_with(portnumber)
        # self.assertEqual(3, self.powerManager.PoECounter)

    @patch('PowerManager.Mapper')
    def testEvaluatePoENotif_NoTCConnected(self, mapper):
        self.powerManager.thinClientsInitialized = False
        self.powerManager.PoECounter = 2
        payload = ['\x07', '\x00']

        ret = self.powerManager.evaluatePoENotif(payload)

        self.assertEqual(3, self.powerManager.PoECounter)

    @patch("PowerManager.Mapper")
    def testEvaluatePoENotif_TestMode(self, mapper):
        #TESTMDOE is True by default
        payload = ['\x07', '\x00']
        self.powerManager.PoECounter = 3

        self.powerManager.evaluatePoENotif(payload)

        self.assertEqual(self.powerManager.thinClientsInitialized, True)

    @patch('PowerManager.task')
    @patch('PowerManager.Mapper')
    def testEvaluatePoENotif_TCFinishedInializing(self, mapper, task):
        Conf.MAXCLIENTS = 16
        self.powerManager.PoECounter = 16
        payload = ['\x0F', '\x01']
        self.powerManager.powerUpPoE = Mock()


        ret = self.powerManager.evaluatePoENotif(payload)

        self.assertEqual(self.powerManager.thinClientsInitialized, True)

    @patch('PowerManager.task')
    @patch('PowerManager.Mapper')
    def testEvaluatePoENotif_PowerUpNextPoE(self, mapper, task):
        payload = ['\x07','\x01']
        port = 8
        self.powerManager.powerUpPoE = Mock()

        ret = self.powerManager.evaluatePoENotif(payload)

        self.powerManager.powerUpPoE.assert_called_with(port)

    @patch('PowerManager.Mapper')
    def testEvaluatePoENotif_TCRemovedDuringInitialization(self, mapper):
        self.powerManager.thinClientsInitialized = False
        payload = ['\x07', '\x00']
        self.powerManager.PoECounter = 2

        self.powerManager.evaluatePoENotif(payload)

        self.assertEqual(self.powerManager.PoECounter, 3)

    def testEvaluateRDPRequest_turnOffTC(self):
        payload=['\x08','\x00']
        port = 8
        self.powerManager.powerDownPoE = Mock()

        self.powerManager.evaluateRDPRequest(payload)

        self.powerManager.powerDownPoE.assert_called_with(port)

    @patch('PowerManager.Mapper')
    def testEvaluateRDPRequest_removeTCOnMap(self, mapper):
        payload=['\x08','\x00']
        port = 8
        self.powerManager.powerDownPoE = Mock(return_value=defer.succeed(None))

        self.powerManager.evaluateRDPRequest(payload)

        mapper.removeThinClient.assert_called_with(port)

    def testReceivedRDPRequest(self):
        cmd = []
        cmd.append(Command.RDPREQUEST)
        cmd.append('\x0B') #portnumber
        cmd.append('\x00') #requested power 
        payload = ['\x0B','\x00']
        self.powerManager.evaluateRDPRequest = Mock()

        self.powerManager.processCommand(cmd)

        self.powerManager.evaluateRDPRequest.assert_called_with(payload)

    def testSendNotificationToRDP(self):
        self.powerManager.transport = Mock()
        notif = []

        self.powerManager.sendNotificationToRDP

        self.powerManager.transport.write.assert_called_with(ThinClient)

    testSendNotificationToRDP.skip = "not yet complete"

    def tesReceivedCheckAliveRequest(self):
        cmd = Command.KEEPALIVE
        self.powerManager.transport = Mock()

        self.powerManager.processCommand(cmd)

        self.powerManager.transport.write.assert_called_with(cmd, Switch.IPADDRESS, 8880)

    def testReceivedSwitchReady(self):
        cmd = Command.SWITCHREADY
        payload = '\x0E'
        msg = '\x0C\x0E'

        self.powerManager.processCommand(msg)

        self.assertEqual(self.powerManager.readyPorts, 14)

    def testStartShutdown_ShutdownPostponed(self):
        NodeA.shuttingDownPostponed = True
        NodeB.shuttingDownPostponed = True
        self.powerManager.normalShutdown = Mock()

        self.powerManager.startShutdown()

        self.assertEqual(NodeA.shuttingDownPostponed,False)
        self.assertEqual(NodeB.shuttingDownPostponed,False)
        self.assertEqual(NodeA.serverState, ServerState.COUNTDOWN_IN_PROGRESS)
        self.assertEqual(NodeB.serverState, ServerState.COUNTDOWN_IN_PROGRESS)
        self.assertEqual(self.powerManager.postponeToggle, True)
        assert self.powerManager.normalShutdown.called

    def testPostponeShutdown(self):
        time = '11111'
        intTime = int(time, 16)

        self.powerManager.postponeShutdown(time)

        self.assertEqual(NodeA.shuttingDownPostponed, True)
        self.assertEqual(NodeB.shuttingDownPostponed, True)
        self.assertEqual(self.powerManager.shutdownDelay, intTime)

    def testCancelShutdown(self):
        self.powerManager.cancelShutdown()

        self.assertEqual(NodeA.shuttingDownCancelled, True)
        self.assertEqual(NodeB.shuttingDownCancelled, True)

    def testStartShutdown_Cancelled(self):
        NodeA.serverState = ServerState.ON
        NodeB.shuttingDownCancelled = True

        self.powerManager.startShutdown()

        self.assertEqual(NodeA.shuttingDownCancelled, False)
        self.assertEqual(NodeB.shuttingDownCancelled, False)  

    def testACRestoredCommandReceived_LowPower(self):
        cmd = Command.AC_RESTORED
        Power.state = PowerState.LOWBATTERY
        # Node.upNodeCount = 2
        self.powerManager.ACRestoredFromLowPower = Mock()

        self.powerManager.processCommand(cmd)

        assert self.powerManager.ACRestoredFromLowPower.called

    @patch('PowerManager.utils')
    def testACRestoredFromLowPower(self, utils):
        # self.powerManager.checkWhichNode = Mock(return_value = 'sb.110134.cloudtop.ph')
        
        # params = []
        # params.append('-H')
        # params.append(Switch.IPADDRESS)
        # params.append('-U')
        # params.append(Switch.USERNAME)
        # params.append('-P')
        # params.append(Switch.PASSWORD)
        # params.append('raw')
        # params = tuple(params)

        # self.powerManager.ACRestoredFromLowPower()
        pass

    def testACRestoredFromHighPower(self):
        self.powerManager.ACRestoredFromHighPower()

        self.assertEqual(Power.state, PowerState.AC)

    def testPostponeShutdownReceived(self):
        pass

    def testPostponeShutdownReceived_BatteryMode(self):
        cmd = Command.POSTPONE
        Power.state = PowerState.BATTERYMODE

        self.powerManager.processCommand(cmd)

        self.assertEqual(NodeA.shuttingDownPostponed, False)
        self.assertEqual(NodeB.shuttingDownPostponed, False)


    @patch('PowerManager.task')
    def testStartProtocol_NoScheduling(self, task):
        Conf.SCHEDULESHUTDOWN = False
        self.powerManager.powerUpThinClients = Mock()

        self.powerManager.startProtocol()
        assert not task.deferLater().called


    @patch('PowerManager.utils')
    def testShutdownBothBaremetals(self, utils):
        NodeA.serverState = ServerState.ON
        NodeB.serverState = ServerState.ON
        cmd = 'ssh'
        params1 = []
        params2 = []
        params1.append('root@%s' % NodeA.IPADDRESS)
        params2.append('root@%s' % NodeB.IPADDRESS)
        params1.append('\"poweroff\"')
        params2.append('\"poweroff\"')


        d = self.powerManager.shutdownBothBaremetals()

        # self.assertEqual(NodeA.serverState, ServerState.SHUTDOWN_IN_PROGRESS)
        # self.assertEqual(NodeB.serverState, ServerState.SHUTDOWN_IN_PROGRESS)
        utils.getProcessOutput.assert_has_call(cmd, params1)
        utils.getProcessOutput().addCallback.assert_called_with(utils.getProcessOutput, cmd, params2)

    @patch('PowerManager.timer')
    def testPowerUpThinClients(self, timer):
        self.powerManager.sendIPMICommand = Mock(return_value=defer.succeed(None))
        self.powerManager.sendIPMICommand().addCallback = Mock()
        self.powerManager._logExitValue = Mock()
        calls = []
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
        calls.append(call(params))
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

            calls.append(call(self.powerManager.sendIPMICommand,params))
            calls.append(call(self.powerManager._logExitValue))
        d = self.powerManager.powerUpThinClients()

        self.powerManager.sendIPMICommand.assert_has_calls(calls[0])
        self.powerManager.sendIPMICommand().addCallback.assert_has_calls(calls[1:])
        d.addCallback(self.assertEqual, None)

    def testPowerUpPoE(self):
        self.powerManager.sendIPMICommand = Mock(return_value=defer.succeed(None))

        num = 11
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

        d = self.powerManager.powerUpPoE(num)

        self.powerManager.sendIPMICommand.assert_called_with(params)

    def testPowerDownPoE(self):
        self.powerManager.sendIPMICommand = Mock()
        port = 7
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

        d = self.powerManager.powerDownPoE(port)

        self.powerManager.sendIPMICommand.assert_called_with(params)

    def testPowerDownThinClients(self):
        self.powerManager.sendIPMICommand = Mock(return_value=defer.succeed(None))
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
        
        d = self.powerManager.powerDownThinClients()

        self.powerManager.sendIPMICommand.assert_called_with(params)
        d.addCallback(self.assertEqual, None)

    def testReceivedUpdateTCDatabaseCommand(self):
        cmd = Command.UPDATE
        self.powerManager.updateTCDatabase = Mock()

        self.powerManager.processCommand(cmd)

        assert self.powerManager.updateTCDatabase.called

    @patch('PowerManager.IPAddressFinder')
    def testUpdateTCDatabase(self, finder):
        finder.update = Mock()

        self.powerManager.updateTCDatabase()

        assert finder.update.called

    def testShutdownRequestReceived(self):
        cmd = Command.SHUTDOWN_REQUEST
        self.powerManager.grantShutdownRequest = Mock()

        self.powerManager.processCommand(cmd)

        assert self.powerManager.grantShutdownRequest.called

    def testShutdownRequestReceived_CountdownStarted(self):
        cmd = Command.SHUTDOWN_REQUEST
        self.powerManager.grantShutdownRequest = Mock()
        NodeA.serverstate = ServerState.COUNTDOWN_IN_PROGRESS
        NodeB.serverState = ServerState.COUNTDOWN_IN_PROGRESS

        self.powerManager.processCommand(cmd)

        assert not self.powerManager.grantShutdownRequest.called

    def testGrantShutdownRequest(self):
        pass

    def testReceivedNormalShutdownCommand(self):
        cmd = Command.SHUTDOWN_NORMAL
        self.powerManager.normalShutdown = Mock()

        self.powerManager.processCommand(cmd)
        
        assert self.powerManager.normalShutdown.called

    def testReceivedNormalShutdownCommand_CountdownStarted(self):
        cmd = Command.SHUTDOWN_REQUEST
        self.powerManager.normalShutdown = Mock()
        NodeA.serverstate = ServerState.COUNTDOWN_IN_PROGRESS
        NodeB.serverState = ServerState.COUNTDOWN_IN_PROGRESS

        self.powerManager.processCommand(cmd)

        assert not self.powerManager.normalShutdown.called

    @patch("__builtin__.open")
    def testGetVirtualIP(self, fopen):
        lines = ["127.0.0.1   localhost localhost.localdomain localhost4 localhost4.localdomain4 sb.local"\
            ,"::1         localhost localhost.localdomain localhost6 localhost6.localdomain6"\
            ,""\
            ,"10.18.221.11      sa.105134.cloudtop.ph"\
            ,"10.18.221.24      rdpminta.local"\
            ,"10.18.221.26      virtualip.105134.cloudtop.ph"]
        fopen().readlines = Mock(return_value=lines)
        correctIP = "10.18.221.26"

        ipaddress = self.powerManager.getVirtualIP()

        self.assertEqual(ipaddress, correctIP)

    @patch("PowerManager.telnetlib")
    @patch("PowerManager.Switch")
    def testCheckSwitchState(self, switch, telnet):
        #check state then match with internal state
        switch.IPADDRESS = mock(return_value='10.225.3.210')
        telnet.write = Mock()
        switchMatchString = """
            
            RTCS v3.08.00 Telnet server            

            Shell (build: Oct 26 2013)
            Copyright (c) 2008 Freescale Semiconductor;
            shell>
            shell>
        """

        switchStateString = """
            state is 8
            SOC_state is 3
            VB_state is 4
            pdu logs is 203
            pdu cnt is 48175
            pdu char is [
            ]
            shell>
        """

        telnet.write.assert_has_call("state\n")
        telnet.write.assert_has_call("exit\n")
        ret = self.powerManager.getSwitchState()

        self.assertEqual(ret, 8)

    testCheckSwitchState.skip = "not yet implemented"

    @patch("PowerManager.utils")
    def testLockResources(self, utils):
        cmd = '/usr/sbin/clusvcadm'
        params = []
        params.append('-l')
        utils.getProcessOutput = Mock(return_value=defer.succeed(None))

        d = self.powerManager.lockResources()

        utils.getProcessOutput.assert_called_with(cmd, params)
        d.addCallback(self.assertEqual, None)

    @patch("PowerManager.logging")
    @patch("PowerManager.utils")
    def testLockResources_fail(self, utils, logging):

        d = self.powerManager.lockResources()

        logging.error.assert_called_with('failed to lock cluster resources')

    testLockResources_fail.skip = "errback handling pending"

#PowerManager Factory TestSuite
class PowerManagerFactoryTestSuite(unittest.TestCase):
    def setUp(self):
        self.factory = PowerManagerFactory()

    def tearDown(self):
        pass

    @patch('PowerManager.PowerManager')
    def testBuildProtocol(self, powerManager):
        addr = Mock()

        self.factory.buildProtocol(addr)

        self.assertEqual(self.factory.protocol, powerManager())


class IPMISecurityTestSuite(unittest.TestCase):
    def setUp(self):
        self.ipmiSecurity = IPMISecurity()

    def tearDown(self):
        pass

    def testEncrpyt(self):
        passphrase = 'unusual password' 
        IV = '1234567890abcdef'
        message = 'hello world'

        hashed = self.ipmiSecurity.encrypt(passphrase, IV, message)

        self.assertEqual(hashed, '\xf5\xdc\xb0UU\x13Ti\xf7\xf3\x95')

    @patch('PowerManager.os')
    @patch('__builtin__.open')
    def testGetIPMIPassword(self, opencmd, os):
        opencmd.readline = Mock()
        opencmd().readline.side_effect = ['1234567890abcdef','\xf5\xdc\xb0UU\x13Ti\xf7\xf3\x95']
        self.ipmiSecurity.decrypt = Mock(return_value='wahoooooo')

        self.ipmiSecurity.getIPMIPassword()

        self.ipmiSecurity.decrypt.assert_called_with\
            (self.ipmiSecurity.secretKey, '1234567890abcdef', '\xf5\xdc\xb0UU\x13Ti\xf7\xf3\x95')
        self.assertEqual(self.ipmiSecurity.password,'wahoooooo')        
        
            
    def testDecrypt(self):
        passphrase = 'unusual password' 
        IV = '1234567890abcdef'
        encrypted = '\xf5\xdc\xb0UU\x13Ti\xf7\xf3\x95'

        password = self.ipmiSecurity.decrypt(passphrase, IV, encrypted)   

        self.assertEqual(password, 'hello world')

    @patch('PowerManager.os')
    @patch('__builtin__.open')
    def testStoreIPMIPassword(self, Open, os):
        self.ipmiSecurity.encrypt = Mock(return_value='wahooooo')
        self.ipmiSecurity.password = 'IPMIPassword'
        os.urandom = Mock(return_value='1234567890abcdef')
        call1 = call('1234567890abcdef')
        call2 = call('wahooooo')
        calls = [call1,call2]

        self.ipmiSecurity.storeIPMIPassword()

        Open().write.assert_has_calls(calls)
        self.ipmiSecurity.encrypt.assert_called_with(self.ipmiSecurity.secretKey\
            , '1234567890abcdef', self.ipmiSecurity.password)
        assert Open().close.called
