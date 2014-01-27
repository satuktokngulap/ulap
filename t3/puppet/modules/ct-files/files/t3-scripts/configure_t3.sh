#!/bin/bash
# CloudTop: T3 2-Node Configuration v0.05
# Sets up configuration files for 2-Node T3 servers
# Author: Isabel Montes

if [ ! $# == 6 ]; then
	echo "Usage: $0 <local IP address> <peer IP address> <local IPMI IP address> <peer IPMI IP address> <Virtual IP> <local hostname>"
	exit 1
fi

MYIP="$1"
MYPEER="$2"
MYIPMI="$3"
PEERIPMI="$4"
VIRTIP="$5"
MYNAME="$6"
MYPEERNAME=""
MYCLUSTER="$(echo $MYNAME | gawk -F'.' '{print $2}')"
if [ "$(echo $MYNAME | gawk -F'.' '{print $1}')" = "sa" ]; then
       MYPEERNAME="sb."$MYCLUSTER".cloudtop.ph";
else MYPEERNAME="sa."$MYCLUSTER".cloudtop.ph";
fi

RDPAIP="$(echo $MYIP | gawk -F'.' '{print $1"."$2"."$3".24"}')"
RDPBIP="$(echo $MYIP | gawk -F'.' '{print $1"."$2"."$3".25"}')"
LDAPIP="$(echo $MYIP | gawk -F'.' '{print $1"."$2"."$3".20"}')"
LMSIP="$(echo $MYIP | gawk -F'.' '{print $1"."$2"."$3".21"}')"

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

PRELIMPATH="${DIR}/preliminaries/"
DRBDPATH="${DIR}/drbd/"
CLUSPATH="${DIR}/cluster/"
LVMPATH="${DIR}/lvm/"

PRELIMS="${PRELIMPATH}install_preliminaries.sh"


# Test an IP address for validity:
# Usage:
#      valid_ip IP_ADDRESS
#      if [[ $? -eq 0 ]]; then echo good; else echo bad; fi
#   OR
#      if valid_ip IP_ADDRESS; then echo good; else echo bad; fi
# Source: http://www.linuxjournal.com/content/validating-ip-address-bash-script
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

echo "-----------------"
echo "Configuring node..."

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

sed -e 's/MY_IP/'$MYIP'/g'\
    -e 's/MY_PEER/'$MYPEER'/g'\
    -e 's/MY_NAME/'$MYNAME'/g'\
    -e 's/PEER_NAME/'$MYPEERNAME'/g'\
    -e 's/IPMI_LO/'$MYIPMI'/g'\
    -e 's/IPMI_RE/'$PEERIPMI'/g'\
    -e 's/LOCAL_IPMI_NAME/'ipmi.$MYNAME'/g'\
    -e 's/PEER_IPMI_NAME/'ipmi.$MYPEERNAME'/g' < ${PRELIMPATH}hosts > /tmp/hosts

cp /etc/hosts /etc/hosts.bak
cp /tmp/hosts /etc/hosts

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

echo "Updating cluster.conf..."
sed -e 's/SITE_ID/'$MYCLUSTER'/g' -e 's/VIRT_IP/'$VIRTIP'/g' -e 's/RDPA_IP/'$RDPAIP'/g' -e 's/RDPB_IP/'$RDPBIP'/g' -e 's/LDAP_IP/'$LDAPIP'/g' -e 's/LMS_IP/'$LMSIP'/g' < ${CLUSPATH}cluster.conf > /tmp/cluster.conf

mv /tmp/cluster.conf /etc/cluster/cluster.conf

echo "Configuring LVM2-cluster..."
cp /etc/lvm/lvm.conf /etc/lvm/lvm.conf.bak
cp ${LVMPATH}lvm.conf /etc/lvm/lvm.conf

echo "Copying vm_autostart..."
cp ${PRELIMPATH}start_vm.sh /root/start_vm.sh

echo "Copying rambo..."
mkdir /root/scripts
cp ${PRELIMPATH}rambo /root/scripts/rambo

echo "Done! Please check configuration files before proceeding"
ls -ltr /etc/hosts*
ls -ltr /etc/cluster/cluster.conf*
ls -ltr /etc/drbd.d/*
ls -ltr /etc/lvm/lvm.conf*
