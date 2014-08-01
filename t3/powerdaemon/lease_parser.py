#Python script for parsing DHCP Lease for the latest ThinClient to get IP Address from DHCP
#Output of the script should be a string for simplicity
#Author: Gene Paul L. Quevedo

from parse import *
import sys

#logic of parsing DHCP lease
ipaddress = None
HWaddress = None

leaseFile = open("/var/lib/dhcpd/dhcpd.leases")

for line in leaseFile:
    ipstring = parse("lease {} {", line)
    if ipstring is not None:
        ipaddress = ipstring[0]
    hwstring = parse("  hardware ethernet {};", line)
    if hwstring is not None:
    	HWaddress = hwstring[0]

values = "%s,%s" % (ipaddress, HWaddress)

sys.exit(values)