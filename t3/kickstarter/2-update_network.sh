#!/bin/bash
# CloudTop: T3 2-Node DRBD Configuration v0.02
# This script sets up network configuration files for 2-Node T3 servers
# Basically, this modifies default interfaces and creates
# network bridge interfaces.
#
# Author: Kenan Virtucio
# Date: February 25, 2014

sed -i 's/\"//g' /etc/sysconfig/network-scripts/ifcfg-eth0
sed -i 's/\"//g' /etc/sysconfig/network-scripts/ifcfg-eth1
sed -i 's/NM_CONTROLLED\=yes/NM_CONTROLLED\=no/g' /etc/sysconfig/network-scripts/ifcfg-eth0
sed -i 's/NM_CONTROLLED\=yes/NM_CONTROLLED\=no/g' /etc/sysconfig/network-scripts/ifcfg-eth1
sed -i 's/UUID/#UUID/g' /etc/sysconfig/network-scripts/ifcfg-eth0
sed -i 's/UUID/#UUID/g' /etc/sysconfig/network-scripts/ifcfg-eth1
sed -i 's/HWADDR/#HWADDR/g' /etc/sysconfig/network-scripts/ifcfg-eth0
sed -i 's/HWADDR/#HWADDR/g' /etc/sysconfig/network-scripts/ifcfg-eth1
sed -i 's/BOOTPROTO\=static/BOOTPROTO\=none/g' /etc/sysconfig/network-scripts/ifcfg-eth1

cp /etc/sysconfig/network-scripts/ifcfg-eth0 /etc/sysconfig/network-scripts/ifcfg-br0
cp /etc/sysconfig/network-scripts/ifcfg-eth1 /etc/sysconfig/network-scripts/ifcfg-br1

sed -i '/IPADDR/d' /etc/sysconfig/network-scripts/ifcfg-eth0
sed -i '/NETMASK/d' /etc/sysconfig/network-scripts/ifcfg-eth0
sed -i '/GATEWAY/d' /etc/sysconfig/network-scripts/ifcfg-eth0
sed -i '/DNS1/d' /etc/sysconfig/network-scripts/ifcfg-eth0
sed -i '/DNS2/d' /etc/sysconfig/network-scripts/ifcfg-eth0

sed -i 's/BOOTPROTO\=static/BOOTPROTO\=none/g' /etc/sysconfig/network-scripts/ifcfg-eth0
echo "VLAN=yes" >> /etc/sysconfig/network-scripts/ifcfg-eth0
echo "BRIDGE=br0" >> /etc/sysconfig/network-scripts/ifcfg-eth0
echo "BRIDGE=br1" >> /etc/sysconfig/network-scripts/ifcfg-eth1
sed -i 's/DEVICE\=eth0/DEVICE\=br0/g' /etc/sysconfig/network-scripts/ifcfg-br0
sed -i 's/DEVICE\=eth1/DEVICE\=br1/g' /etc/sysconfig/network-scripts/ifcfg-br1
sed -i 's/TYPE\=Ethernet/TYPE\=Bridge/g' /etc/sysconfig/network-scripts/ifcfg-br0
sed -i 's/TYPE\=Ethernet/TYPE\=Bridge/g' /etc/sysconfig/network-scripts/ifcfg-br1
echo "DEFROUTE=yes" >> /etc/sysconfig/network-scripts/ifcfg-br0
echo "DELAY=0" >> /etc/sysconfig/network-scripts/ifcfg-br0
echo "STP=yes" >> /etc/sysconfig/network-scripts/ifcfg-br0



