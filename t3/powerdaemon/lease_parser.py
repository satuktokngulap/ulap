#Python script for parsing DHCP Lease for the latest ThinClient to get IP Address from DHCP
#Output of the script should be a string for simplicity
#Author: Gene Paul L. Quevedo

# from parse import *
import sys
import re

#logic of parsing DHCP lease
ipaddress = None
HWaddress = None

leaseFile = open("/var/lib/dhcpd/dhcpd.leases")

for line in leaseFile:
	ipstring = re.findall('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', line)
    if ipstring is not None:
        ipaddress = ipstring[0]
    hwstring = re.findall('[0-9a-z]{2}:[0-9a-z]{2}:[0-9a-z]{2}:[0-9a-z]{2}:[0-9a-z]{2}:[0-9a-z]{2}', line)
    if hwstring is not None:
    	HWaddress = hwstring[0]

values = "%s,%s" % (ipaddress, HWaddress)

print values
sys.exit(0)