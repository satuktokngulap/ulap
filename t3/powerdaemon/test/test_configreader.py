from mock import Mock, call, patch
from twisted.internet import defer, reactor
from twisted.trial import unittest

from powermodels import NodeA, NodeB, Conf, Switch, ThinClient
from powermodels import MgmtVM
import configreader

# from cloudtop.config.test import TEST

import ConfigParser

class ConfigreaderTestSuite(unittest.TestCase):
    
    def setUp(self):
        self.testFile = "/Users/genepaulquevedo/ulap/t3/powerdaemon/test/artifacts/power_mgmt.cfg"
        switch = {}
        nodeA = {}
        nodeB = {}
        mgmt = {}
        thinclient = {}
        defaults = {}
        self.configset = {}

        switch['id'] = 0x300000
        switch['ipaddress'] = '11.18.221.210'
        switch['username'] = 'Admin'
        switch['password'] = 'Admin'

        nodeA['ip'] = '11.18.221.11'
        nodeA['ipmihost'] = '11.18.221.111'
        nodeA['ipmiuser'] = 'ADMIN'
        nodeA['ipmipassword'] = 'Admin@123'

        nodeB['ip'] = '11.18.221.12'
        nodeB['ipmihost'] = '11.18.221.112'
        nodeB['ipmiuser'] = 'ADMIN'
        nodeB['ipmipassword'] = 'Admin@123'

        mgmt['ip'] = '10.225.3.146'

        thinclient['default_addr'] = ('173.16.1.5', 8880)
        thinclient['serverA_addr'] = ('173.16.1.5', 8880)
        thinclient['serverB_addr'] = ('173.16.1.6', 8880)

        defaults['shutdownhour'] = 20
        defaults['shutdownminute'] = 0
        defaults['wakeuphour'] = 5
        defaults['wakeupminute'] = 0
        defaults['scheduleshutdown'] = True
        defaults['testmode'] = True
        defaults['mapfile'] = '/var/lib/powerdaemon/pmd_DB.sql'

        self.configset['switch'] = switch
        self.configset['nodeA'] = nodeA
        self.configset['nodeB'] = nodeB
        self.configset['thinclient'] = thinclient
        self.configset['mgmt'] = mgmt
        self.configset['defaults'] = defaults

    def tearDown(self):
        pass

    def testFillSwitchDefaults(self):
        configreader._fillSwitchDefaults(self.testFile)

        #checks
        self.assertEqual(Switch.ID, self.configset['switch']['id'])
        self.assertEqual(Switch.IPADDRESS, self.configset['switch']['ipaddress'])
        self.assertEqual(Switch.PASSWORD, self.configset['switch']['password'])

    def testFillConfigDefaults(self):
        configreader._fillConfigDefaults(self.testFile)

        #checks
        self.assertEqual(Conf.SHUTDOWNHOUR, self.configset['defaults']['shutdownhour'])
        self.assertEqual(Conf.SHUTDOWNMINUTE, self.configset['defaults']['shutdownminute'])
        self.assertEqual(Conf.WAKEUPHOUR, self.configset['defaults']['wakeuphour'])
        self.assertEqual(Conf.WAKEUPMINUTE, self.configset['defaults']['wakeupminute'])
        self.assertEqual(Conf.SCHEDULESHUTDOWN, self.configset['defaults']['scheduleshutdown'])
        self.assertEqual(Conf.TESTMODE, self.configset['defaults']['testmode'])
        self.assertEqual(Conf.MAPFILE, self.configset['defaults']['mapfile'])

    def testFillNodeDefaults(self):
        configreader._fillNodeDefaults(self.testFile)

        #checks
        self.assertEqual(NodeA.IP, self.configset['nodeA']['ip'])
        self.assertEqual(NodeA.IPMIHOST, self.configset['nodeA']['ipmihost'])
        self.assertEqual(NodeA.IPMIUSER, self.configset['nodeA']['ipmiuser'])
        self.assertEqual(NodeA.IPMIPASSWORD, self.configset['nodeA']['ipmipassword'])

        self.assertEqual(NodeB.IP, self.configset['nodeB']['ip'])
        self.assertEqual(NodeB.IPMIHOST, self.configset['nodeB']['ipmihost'])
        self.assertEqual(NodeB.IPMIUSER, self.configset['nodeB']['ipmiuser'])
        self.assertEqual(NodeB.IPMIPASSWORD, self.configset['nodeB']['ipmipassword'])
   
    def testFillMgmtDefaults(self):
        configreader._fillNodeDefaults(self.testFile)

        self.assertEqual(MgmtVM.IPADDRESS, self.configset['mgmt']['ip'])


    def testFillThinclientDefaults(self):
        configreader._fillThinclientDefaults(self.testFile)

        self.assertEqual(ThinClient.DEFAULT_ADDR, self.configset['thinclient']['default_addr'])
        self.assertEqual(ThinClient.SERVERA_ADDR, self.configset['thinclient']['serverA_addr'])
        self.assertEqual(ThinClient.SERVERB_ADDR, self.configset['thinclient']['serverB_addr'])

    @patch('configreader._fillSwitchDefaults')
    @patch('configreader._fillNodeDefaults')
    @patch('configreader._fillThinclientDefaults')
    @patch('configreader._fillConfigDefaults')
    def testFillAllDefaults(self, config, thinclient, node, switch):
        configreader.fillAllDefaults(self.testFile)

        configreader._fillSwitchDefaults.assert_called_with(self.testFile)
        configreader._fillConfigDefaults.assert_called_with(self.testFile)
        configreader._fillNodeDefaults.assert_called_with(self.testFile)
        configreader._fillThinclientDefaults.assert_called_with(self.testFile)       