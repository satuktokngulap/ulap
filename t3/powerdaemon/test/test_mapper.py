#Unit Test for Mapper class

from mock import Mock, call, patch, MagicMock
from twisted.internet import defer, reactor
from twisted.trial import unittest

import mapper

import subprocess, shlex

from powermodels import ThinClient, Session

class MapperTestsuite(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        mapper.Mapper.thinClientsList = []
        #reloading module to remove Mock object assignments
        reload(subprocess)
        reload(mapper)

    #top level function for new updates
    #triggered by notification from switchx
    #or ThinClient
    def testUpdateMap(self):
        pass

    def testInializeMap(self):
        pass

    #top level function during initial bootup
    #creates ThinClient objects.
    @patch('mapper.ThinClient')
    def testAddNewThinClient(self, thinclient):
        # mapper.Mapper.getDHCPDetails = Mock(return_value = ('10.225.1.1', '40:d8:55:0c:11:0a'))
        mapper.Mapper.getTouple = Mock(return_value=defer.succeed(('10.225.1.1', '40:d8:55:0c:11:0a')))
        mapper.Mapper.getDHCPDetails = Mock(return_value=defer.succeed(None))
        portnum = 1

        d = mapper.Mapper.addNewThinClient(portnum)

        thinclient.assert_called_with(('10.225.1.1','40:d8:55:0c:11:0a'), portnum)
        self.assertEqual(mapper.Mapper.thinClientsList[0], thinclient())
        assert mapper.Mapper.getDHCPDetails.called 

    testAddNewThinClient.skip = 'change to callback style'

    #TODO: separate into 4 unit tests
    @patch('mapper.ThinClientHandler')
    def testAddNewThinClient(self, tchandler):
        mapper.Mapper.getTouple = Mock(return_value=defer.succeed(('10.225.1.1', '40:d8:55:0c:11:0a')))
        mapper.Mapper.getDHCPDetails = Mock(return_value=defer.succeed(None))
        mapper.Mapper.addTCToList = Mock(return_value=defer.succeed('begin'))
        tchandler.addThinClient = Mock(return_value=defer.succeed('end'))
        mapper.Mapper.sendMapToRDP = Mock(return_value=defer.succeed('true'))
        portnum = 9

        d = mapper.Mapper.addNewThinClient(portnum)

        d.addCallback(self.assertEqual, 'true')

    #wrapper for dhcpd parser. Output: ipaddress,mac-address tuple
    @patch('mapper.utils')
    def testGetDHCPDetails(self, utils):
        cmd = '/usr/bin/ssh' 
        params = ' -o "StrictHostKeyChecking no" root@10.18.221.21 "python /opt/lease_parser.py"'
        params = shlex.split(params)
        utils.getProcessOutput = Mock(return_value=defer.succeed(None))

        d = mapper.Mapper.getDHCPDetails()

        utils.getProcessOutput.assert_called_with(cmd, params)
        d.addCallback(self.assertEqual, None)

    @patch('mapper.os')
    @patch('__builtin__.open')
    def testGetTouple_fileRemoved(self, fileopen, os):
        TCID = '172.16.1.10,40:d8:55:0c:11:0a'
        fileopen().readline = Mock(return_value=TCID)

        ret = mapper.Mapper.getTouple()

        os.remove.assert_called_with('/tmp/touple')

    testGetTouple_fileRemoved.skip = "not performed"
    
    @patch('mapper.os')
    @patch('__builtin__.open')
    def testGetTouple_returnDeferred(self, fileopen, os):
        TCID = '172.16.1.10,40:d8:55:0c:11:0a\n'
        tupleID = ('172.16.1.10','40:d8:55:0c:11:0a')
        # fileopen().readline = Mock(return_value=TCID)

        d = mapper.Mapper.getTouple((TCID))

        d.addCallback(self.assertEqual, tupleID)
    
    @patch('mapper.ThinClient')
    def testAddTCToList_correctObject(self, tc):
        touple = ('10.18.221.25', '40:d8:55:0c:11:0a')
        port = 8

        d = mapper.Mapper.addTCToList(touple, port)

        self.assertEqual(mapper.Mapper.thinClientsList[0], tc())

    @patch('mapper.ThinClient')
    def testAddTCToList_correctParams(self, tc):
        touple = ('10.18.221.25', '40:d8:55:0c:11:0a')
        port = 8
        
        d = mapper.Mapper.addTCToList(touple, port)

        tc.assert_called_with(touple, port)
    
    @patch('mapper.ThinClient')
    @patch('mapper.defer')
    def testAddTCToList_returnTCObject(self, defer, tc):
        touple = ('10.18.221.25', '40:d8:55:0c:11:0a')
        port = 8

        d = mapper.Mapper.addTCToList(touple, port)

        d.addCallback(self.assertEqual, tc())

    #should not happen since thinclient is deleted as soon as it is disconnected
    @patch('mapper.ThinClient')
    def testAddTCToList_sameThinClient(self, tc):
        pass

    @patch('mapper.ThinClientHandler')
    def testRemoveThinClient(self, tchandler):
        portnum = 7
        tc = Mock()
        tc.port = portnum
        mapper.Mapper.thinClientsList = [tc]
        mapper.Mapper.sendMapToRDP = Mock(return_value=defer.succeed(None))


        mapper.Mapper.removeThinClient(portnum)

        self.assertEqual(len(mapper.Mapper.thinClientsList), 0)

    @patch('mapper.ThinClientHandler')
    def testRemoveThinClient_removeFromDB(self, tchandler):
        portnum = 7
        tc = Mock()
        tc.port = portnum
        mapper.Mapper.thinClientsList = [tc]
        mapper.Mapper.sendMapToRDP = Mock(return_value=defer.succeed(None))


        mapper.Mapper.removeThinClient(portnum)

        tchandler.removeThinClient.assert_called_with(tc)

    @patch('mapper.ThinClientHandler')
    def testRemoveThinClient_updateJSON(self, tchandler):
        portnum = 7
        tc = Mock()
        tc.port = portnum
        mapper.Mapper.thinClientsList = [tc]
        mapper.Mapper.sendMapToRDP = Mock(return_value=defer.succeed(None))

        d = mapper.Mapper.removeThinClient(portnum)

        d.addCallback(self.assertEqual, None)

    @patch('mapper.ThinClient')
    def testAddNullThinClient(self, tc):
        portnum = 6

        mapper.Mapper.addNullThinClient(portnum)

        # tc = mapper.Mapper.thinClientsList[-1]
        tc.assert_called_with((None,None), portnum)     

    #wrapper for calling XFinger

    @patch('mapper.utils.getProcessOutput')
    def testGetRDPSessionsViaXFinger(self, process):
        cmd = '/usr/bin/ssh'
        paramsRDP1 = '-o "StrictHostKeyChecking no" root@10.18.221.23 "python /opt/xfinger.sh"'
        paramsRDP2 = '-o "StrictHostKeyChecking no" root@10.18.221.24 "python /opt/xfinger.sh"'
        paramsRDP1 = shlex.split(paramsRDP1)
        paramsRDP2 = shlex.split(paramsRDP2)
        call1 = call(cmd, paramsRDP1)
        call2 = call(cmd, paramsRDP2)
        calls_list = [call1, call2]

        d = mapper.Mapper.getRDPSessionsViaXFinger()

        process.assertEqual_has_calls(calls_list)

    #receives a list of tuple --> ([True/False], value)
    def testParseXFingerResults(self):
        testString1 = 'UID=student20 PID=2128 IP= 172.16.1.130\nUID=student27 PID=3126 IP=172.16.1.142'
        testString2 = 'UID=student21 PID=2138 IP= 172.16.1.131\nUID=student28 PID=3136 IP=172.16.1.143'
        results = [(True, testString1), (True, testString2)]
        validList = [{"sessionid": 2128, "userid": 'student20', "ipaddress": '172.16.1.130'}\
        ,{"sessionid": 3126, "userid": "student27", "ipaddress":'172.16.1.142' }\
        ,{"sessionid": 2138, "userid": "student21", "ipaddress":'172.16.1.131' }\
        ,{"sessionid": 3136, "userid": "student28", "ipaddress": '172.16.1.143' }]
    
        sessionList = mapper.Mapper.parseXFingerResults(results)

        self.assertEqual(sessionList, validList)

    @patch('mapper.Session')
    def testUpdateSessionList_correctObjectCall(self, session):
        sessionList = [{"sessionid": 2128, "userid": 'student20', "ipaddress": '172.16.1.130'}\
        ,{"sessionid": 3126, "userid": "student27", "ipaddress":'172.16.1.142' }\
        ,{"sessionid": 2138, "userid": "student21", "ipaddress":'172.16.1.131' }\
        ,{"sessionid": 3136, "userid": "student28", "ipaddress": '172.16.1.143' }]
        validSessionList = [{}, {}]
        callList = [call(2128,'student20'), call(3126, 'student27')\
            ,call(2138, 'student21')\
            ,call(3136,'student28')]

        mapper.Mapper.updateSessionList(sessionList)

        session.assert_has_calls(callList)

    #for improvement
    @patch('mapper.Session')
    def testUpdateSessionList_appendToList(self, session):
        sessionList = [{"sessionid": 2128, "userid": 'student20', "ipaddress": '172.16.1.130'}]

        mapper.Mapper.updateSessionList(sessionList)

        assert isinstance(mapper.Mapper.sessionList[0], Mock)

    @patch('mapper.Session')
    def testUpdateSessionList_emptyListFirst(self, session):
        #inject empty list to test
        sessionList = []
        #pretent sessionList is not empty
        mapper.Mapper.sessionList = [1,2,3]

        mapper.Mapper.updateSessionList(sessionList)

        assert not mapper.Mapper.sessionList

    def testUpdateThinClient_addSessionID(self):
        tc = Mock(ipAddress='172.16.1.23', port=9)
        def setSession():
            tc.sessionID = 2128
        tc.setSessionID = Mock(side_effect=setSession())
        mapper.Mapper.thinClientsList.append(tc)
        session = {"sessionid": 2128, "userid": 'student20', "ipaddress": '172.16.1.130'}

        mapper.Mapper.updateThinClientSessionAttribute(session)

        self.assertEqual(tc.sessionID, session["sessionid"])

    def testUpdateSessions_callGetRDPSessionViaXFinger(self):
        mapper.Mapper.getRDPSessionsViaXFinger = Mock()
        mapper.Mapper.updateSessionListAndAttributes = Mock()

        d = mapper.Mapper.updateSessions()

        assert mapper.Mapper.getRDPSessionsViaXFinger.called

    def testUpdateSessions_callUpdateSessionListAndAttributes(self):
        dummyxfingerresults = []
        mapper.Mapper.getRDPSessionsViaXFinger = Mock(return_value = defer.succeed(dummyxfingerresults))
        mapper.Mapper.updateSessionListAndAttributes = Mock()

        d = mapper.Mapper.updateSessions()

        mapper.Mapper.updateSessionListAndAttributes.assert_called_with(dummyxfingerresults)

    def testUpdateSessionListAndAttributes_callParseXFingerResults(self):
        sessionstrings ="dummy xfinger results"
        mapper.Mapper.parseXFingerResults = MagicMock()
        mapper.Mapper.updateSessionList = Mock()
        mapper.Mapper.updateThinClientSessionAttribute = Mock()

        mapper.Mapper.updateSessionListAndAttributes(sessionstrings)

        mapper.Mapper.parseXFingerResults.assert_called_with(sessionstrings)

    def testUpdateSessionListAndAttributes_callUpdateSessionList(self):
        sessionstrings ="dummy xfinger results"
        sessionList = ['s1', 's2']
        mapper.Mapper.parseXFingerResults = MagicMock(return_value=sessionList)
        mapper.Mapper.updateSessionList = Mock()
        mapper.Mapper.updateThinClientSessionAttribute = Mock()


        mapper.Mapper.updateSessionListAndAttributes(sessionstrings)

        mapper.Mapper.updateSessionList.assert_called_with(sessionList)

    def testUpdateSessionListAndAttributes_callUpdateThinClientSessionAttribute(self):
        sessionstrings ="dummy xfinger results"
        sessionList = ['s1', 's2']
        mapper.Mapper.parseXFingerResults = MagicMock(return_value=sessionList)
        mapper.Mapper.updateSessionList = Mock()
        mapper.Mapper.updateThinClientSessionAttribute = Mock()
        callList = [call('s1'), call('s2')]

        mapper.Mapper.updateSessionListAndAttributes(sessionstrings)

        mapper.Mapper.updateThinClientSessionAttribute.assert_has_calls(callList)

    def testGetSessionIPGivenSessionID(self):
        ID = 'student20'
        testString = 'UID=student20 PID=2128 IP=172.16.1.130\nUID=student27 PID=3126 IP=172.16.1.142'

        IPaddress = mapper.Mapper.getSessionIPGivenSessionID(testString, ID)

        self.assertEqual(IPaddress, '172.16.1.130')

    def testResetLeases(self):
        #note: Mgmt VM will not start right away
        pass    

    #pass
    def testSearchByMacAddress(self):
        pass

    #pass
    def testSearchBySessionID(self):
        pass

    def testSendMapToRDP(self):
        sampleOutput = [{'ip': '172.18.1.101', 'mac':'od:23:2x:df:hh:k9:nb', 'port': 9}]
        mapper.Mapper.createSerializedThinClientData = Mock(return_value=sampleOutput)
        mapper.Mapper.writeDataToFile = Mock()
        mapper.Mapper.sendJSONDataToRDP = Mock(return_value=defer.succeed("success"))

        d = mapper.Mapper.sendMapToRDP()

        mapper.Mapper.writeDataToFile.assert_called_with(sampleOutput)
        d.addCallback(self.assertEqual, "success")

    #this test assumes correct constructor for ThinClient object
    #should be using mocks instead
    def testCreateSerializedThinClientData(self):
        tc1 = ThinClient(('172.16.1.81', 'qw:ir:as:df:12:34:56'), 7, None)
        tc2 = ThinClient(('172.16.1.82', 'qw:ir:ad:sf:12:34:56'), 8, None)
        mapper.Mapper.thinClientsList = [tc1, tc2]
        expected = [{'ip': '172.16.1.81' ,'mac': 'qw:ir:as:df:12:34:56','port':7, 'sessionid': None}\
            ,{'ip':'172.16.1.82','mac':'qw:ir:ad:sf:12:34:56','port':8, 'sessionid': None}]

        outputData = mapper.Mapper.createSerializedThinClientData()

        self.assertEqual(outputData, expected)

    @patch('mapper.json')
    @patch('__builtin__.open')
    def testWriteDataToFile(self, fileopen, json):
        data = [{},{}]

        mapper.Mapper.writeDataToFile(data)

        fileopen().write.assert_called_with(json.dumps())

    @patch('mapper.json')
    @patch('__builtin__.open')
    def testWriteDataToFile_correctJsonCall(self,fileopen, json):
        data = [{},{}]

        mapper.Mapper.writeDataToFile(data)

        json.dumps.assert_called_with(data, sort_keys=True, indent=4, \
                separators=(',',':'))

    @patch('mapper.defer.DeferredList')
    @patch('mapper.utils.getProcessOutput')
    def testSendDataToRDPServers_correctgetProcess(self, process, deferredlist):
        cmd = '/usr/bin/scp'
        params1=['/tmp/map.json', 'rdpadmin@%s:/tmp' % ThinClient.SERVERA_ADDR[0]]
        params2=['/tmp/map.json', 'rdpadmin@%s:/tmp' % ThinClient.SERVERB_ADDR[0]]
        call1 = call(cmd, params1)
        call2 = call(cmd, params2)
        calls_list = [call1, call2]

        d =mapper.Mapper.sendJSONDataToRDP()

        process.assert_has_calls(calls_list)

    @patch('mapper.defer.DeferredList')
    @patch('mapper.utils.getProcessOutput')
    def testSendDataToRDPServers_correctdeferredList(self, process, deferredlist):

        d = mapper.Mapper.sendJSONDataToRDP()

        deferredlist.assert_called_with([process(), process()])

    #call a deferLater to try again
    def testSendDataToRDPServer_SCPFails(self):
        pass
