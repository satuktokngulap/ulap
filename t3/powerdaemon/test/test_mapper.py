#Unit Test for Mapper class

from mock import Mock, call, patch, MagicMock
from twisted.internet import defer, reactor
from twisted.trial import unittest

import mapper

import subprocess, shlex

from powermodels import ThinClient

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
    def testGetRDPSessionDetails(self, process):
        cmd = '/usr/bin/ssh'
        paramsRDP1 = '-o "StrictHostKeyChecking no" root@10.18.221.23 "python /opt/xfinger.sh"'
        paramsRDP2 = '-o "StrictHostKeyChecking no" root@10.18.221.24 "python /opt/xfinger.sh"'
        paramsRDP1 = shlex.split(paramsRDP1)
        paramsRDP2 = shlex.split(paramsRDP2)
        call1 = call(cmd, paramsRDP1)
        call2 = call(cmd, paramsRDP2)
        calls_list = [call1, call2]

        d = mapper.Mapper.getRDPSessionDetails()

        process.assertEqual_has_calls(calls_list)

    #receives a list of tuple --> ([True/False], value)
    def testParseXFingerResults(self):
        testString1 = 'UID=student20 PID=2128 IP= 172.16.1.130\nUID=student27 PID=3126 IP= 172.16.1.142'
        testString2 = 'UID=student21 PID=2138 IP= 172.16.1.131\nUID=student28 PID=3136 IP= 172.16.1.143'
        results = [(True, testString1), (True, testString2)]
        validList = [{"sessionid": 2128, "userid": 'student20', "ipaddress": '172.16.1.130'}\
        ,{"sessionid": 3126, "userid": "student27", "ipaddress":'172.16.1.142' }\
        ,{"sessionid": 2138, "userid": "student21", "ipaddress":'172.16.1.131' }\
        ,{"sessionid": 3136, "userid": "student28", "ipaddress": '172.16.1.143' }]
    
    
        sessionList = mapper.Mapper.parseXFingerResults(results)

        self.assertEqual(sessionList, validList)


    testParseXFingerResults.skip ='pending for implementation'

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
        tc1 = ThinClient(('172.16.1.81', 'qw:ir:as:df:12:34:56'), 7)
        tc2 = ThinClient(('172.16.1.82', 'qw:ir:ad:sf:12:34:56'), 8)
        mapper.Mapper.thinClientsList = [tc1, tc2]
        expected = [{'ip': '172.16.1.81' ,'mac': 'qw:ir:as:df:12:34:56','port':7}\
            ,{'ip':'172.16.1.82','mac':'qw:ir:ad:sf:12:34:56','port':8}]

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
