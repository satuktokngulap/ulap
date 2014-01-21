#!/bin/bash
# CloudTop: T3 2-Node DRBD Configuration v0.05
# This script sets up configuration files for 2-Node T3 servers
# It accepts IP address arguments (See usage below), and parses these into
# template configuration files before copying them into the
# appropriate directories
#
# Author: Isabel Montes

# Requires the command to be supplied with 6 arguments:
# Local IP address
# IP address of the peer server
# Local IPMI IP address
# IPMI IP address of the peer server
# Virtual IP address
# Hostname of the local server
if [ ! $# == 6 ]; then
	echo "Usage: $0 <local IP address> <peer IP address> <local IPMI IP address> <peer IPMI IP address> <Virtual IP> <local hostname>"
	exit 1
fi

# Assign names to arguments for easier referencing
MYIP="$1"
MYPEER="$2"
MYIPMI="$3"
PEERIPMI="$4"
VIRTIP="$5"
MYNAME="$6"
MYPEERNAME=""
# Extract school id from the hostname, this will be used to define
# the cluster name
MYCLUSTER="$(echo $MYNAME | gawk -F'.' '{print $2}')"

# If this server is node "sa", then the peer server must be "sb"
if [ "$(echo $MYNAME | gawk -F'.' '{print $1}')" = "sa" ]; then
       MYPEERNAME="sb."$MYCLUSTER".cloudtop.ph";
else MYPEERNAME="sa."$MYCLUSTER".cloudtop.ph";
fi

# Define the VMs' IP addresses based on the local host IP address
# This assumes that all the VMs are in the same 255.255.255.0 subnet
# By default, the T3 2-node DRBD builds follow this convention for
# assigning the VMs' IP addresses:
#	LDAP VM - <subnet>.20
#	LMS VM	- <subnet>.21
#	RDP A VM- <subnet>.24
#	RDP B VM- <subnet>.25
RDPAIP="$(echo $MYIP | gawk -F'.' '{print $1"."$2"."$3".24"}')"
RDPBIP="$(echo $MYIP | gawk -F'.' '{print $1"."$2"."$3".25"}')"
LDAPIP="$(echo $MYIP | gawk -F'.' '{print $1"."$2"."$3".20"}')"
LMSIP="$(echo $MYIP | gawk -F'.' '{print $1"."$2"."$3".21"}')"

# The current directory
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Locations of the dependencies
PRELIMPATH="${DIR}/preliminaries/"
DRBDPATH="${DIR}/drbd/"
CLUSPATH="${DIR}/cluster/"
LVMPATH="${DIR}/lvm/"
LIBVIRTPATH="${DIR}/libvirt/"
PRELIMS="${PRELIMPATH}install_preliminaries.sh"

# Source: http://www.linuxjournal.com/content/validating-ip-address-bash-script
# Test an IP address for validity:
# Usage:
#      valid_ip IP_ADDRESS
#      if [[ $? -eq 0 ]]; then echo good; else echo bad; fi
#   OR
#      if valid_ip IP_ADDRESS; then echo good; else echo bad; fi
function valid_ip()
{
    local  ip=$1
    local  stat=1

    if [[ $ip =~ ^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$ ]]; then
        OIFS=$IFS
        IFS='.'
        ip=($ip)
        IFS=$OIFS
        [[ ${ip[0]} -le 255 && ${ip[1]} -le 255 \
            && ${ip[2]} -le 255 && ${ip[3]} -le 255 ]]
        stat=$?
    fi
    return $stat
}

# Begin 
echo "-----------------"
echo "Configuring node..."

# Check if the arguments passed are valid IP addresses
valid_ip $MYIP
if [[ $? -eq 0 ]]; then 
	echo "Local IP Adress is valid";
else 
	echo "Please enter valid IP address for the local node"
	exit 1;
fi

valid_ip $MYPEER
if [[ $? -eq 0 ]]; then
	echo "Remote IP Adress is valid";
else 
	echo "Please enter valid IP address for the remote node"
	exit 1;
fi

valid_ip $MYIPMI
if [[ $? -eq 0 ]]; then
	echo "IPMI Adress is valid";
else 
	echo "Please enter valid IP address for the local IPMI"
	exit 1;
fi

valid_ip $PEERIPMI
if [[ $? -eq 0 ]]; then
	echo "Peer IPMI Adress is valid";
else 
	echo "Please enter valid IP address for the peer IPMI"
	exit 1;
fi

valid_ip $VIRTIP
if [[ $? -eq 0 ]]; then
	echo "Virtual IP Adress is valid";
else 
	echo "Please enter valid IP address for the virtual IP"
	exit 1;
fi

echo "LOCAL IP: $MYIP"
echo "PEER IP: $MYPEER"
echo "LOCAL NODE: $MYNAME"
echo "ClUSTER: $MYCLUSTER"

# Enter the following entries into /etc/hosts file:
#	1. Local IP address and local hostname
#	2. Peer's IP address and peer's hostname
#	3. Local IPMI IP address and ipmi.<local hostname>
#	4. Peer's IPMI IP address and ipmi.<peer's hostname>
# Save the file to /tmp/hosts
sed -e 's/MY_IP/'$MYIP'/g'\
    -e 's/MY_PEER/'$MYPEER'/g'\
    -e 's/MY_NAME/'$MYNAME'/g'\
    -e 's/PEER_NAME/'$MYPEERNAME'/g'\
    -e 's/IPMI_LO/'$MYIPMI'/g'\
    -e 's/IPMI_RE/'$PEERIPMI'/g'\
    -e 's/LOCAL_IPMI_NAME/'ipmi.$MYNAME'/g'\
    -e 's/PEER_IPMI_NAME/'ipmi.$MYPEERNAME'/g' < ${PRELIMPATH}hosts > /tmp/hosts

# Take a backup of the existing /etc/hosts file, and replace 
# it with the file generated into /tmp/hosts
cp /etc/hosts /etc/hosts.bak
cp /tmp/hosts /etc/hosts

# Setup the DRBD configuration files:
# There are 3 configuration files that will be used:
#	1. global_common.conf - global configuration
#	2. r0.res - resource r0 configuration
#	3. r1.res - resource r1 configuration
echo "Configuring DRBD files..."
for FILE in `ls -1 ${DRBDPATH}*`; do
	FILENAME=$(echo ${FILE} | gawk -F'/' '{print $NF}')
	if [ "$(echo $MYNAME | gawk -F'.' '{print $1}')" = "sa" ]; then
       		sed -e 's/SITE_ID/'$MYCLUSTER'/g' -e 's/MY_IP/'$MYIP'/g' -e 's/MY_PEER/'$MYPEER'/g' < $FILE > /tmp/$FILENAME
	else sed -e 's/SITE_ID/'$MYCLUSTER'/g' -e 's/MY_IP/'$MYPEER'/g' -e 's/MY_PEER/'$MYIP'/g' < $FILE > /tmp/$FILENAME;
	fi

	if [ "$FILENAME" = "global_common.conf" ]; then
		cp /etc/drbd.d/global_common.conf /etc/drbd.d/global_common.conf.bak
	fi

	cp /tmp/$FILENAME /etc/drbd.d/$FILENAME

done

# Setting up the cluster.conf file:
# This is where the cluster configuration and rgmanager services
# are defined.
echo "Updating cluster.conf..."
sed -e 's/SITE_ID/'$MYCLUSTER'/g' -e 's/VIRT_IP/'$VIRTIP'/g' -e 's/RDPA_IP/'$RDPAIP'/g' -e 's/RDPB_IP/'$RDPBIP'/g' -e 's/LDAP_IP/'$LDAPIP'/g' -e 's/LMS_IP/'$LMSIP'/g' < ${CLUSPATH}cluster.conf > /tmp/cluster.conf

mv /tmp/cluster.conf /etc/cluster/cluster.conf

# Copy predefined lvm.conf file into the appropriate directory
echo "Configuring LVM2-cluster..."
cp /etc/lvm/lvm.conf /etc/lvm/lvm.conf.bak
cp ${LVMPATH}lvm.conf /etc/lvm/lvm.conf

# Copy predefined libvirtd.conf file into the appropriate directory
echo "Configuring libvirtd..."
cp /etc/libvirt/libvirtd.conf /etc/libvirt/libvirtd.conf.bak
cp ${LIBVIRTPATH}libvirtd.conf /etc/libvirt/libvirtd.conf

# Copy the start_vm.sh file into root directory.
# This is used to start the VMs automatically at startup
echo "Copying vm_autostart..."
cp ${PRELIMPATH}start_vm.sh /root/start_vm.sh

# Copy the rambo scripts into the root directory
# This feature in the T3 setup is currently not enabled
echo "Copying rambo..."
mkdir /root/scripts
cp ${PRELIMPATH}rambo /root/scripts/rambo

echo "Done! Please check configuration files before proceeding"
ls -ltr /etc/hosts*
ls -ltr /etc/cluster/cluster.conf*
ls -ltr /etc/drbd.d/*
ls -ltr /etc/lvm/lvm.conf*
