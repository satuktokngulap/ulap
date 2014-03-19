#!/bin/bash
# CloudTop: T3 2-Node DRBD Configuration v0.02
# This script install default packages for T3 builds
# and update snmpd/ntpd configuration files
#
# Author: Kenan Virtucio
# Date: February 25, 2014

LOGFILE=$EXEC_PWD/logs/install_preliminaries_t3_baremetal-drbd.log.`date +%Y%m%d_%H%M`
# Install Local Repository
echo "Installing Trusted Repository.."
echo
rpm -Uvh http://centosrepo.upd.edu.ph/CentOS/upcentos-0.1-1.el6.x86_64.rpm
sed -i 's/centosrepo.upd.edu.ph/mirror.pregi.net\/pub\/Linux/g' /etc/yum.repos.d/upcentos.repo
if [ $? != 0 ]; then
	echo "Error: occured during install of trusted repository"
	exit
fi
echo "Done installing trusted repository"
echo

echo "Update Packages"
echo
yum update -y
if [ $? != 0 ]; then
        echo "ERROR: occured during update"
        exit
fi
echo "Done installing default packages"
echo

echo "Installing Default Packages.."
echo
yum install -y vim rsyslog net-snmp net-snmp-utils net-snmp-devel ntp sudo vixie-cron crontabs mlocate rsync wget
if [ $? != 0 ]; then
	echo "ERROR: occured during install of default packages"
	exit
fi
echo "Done installing default packages"
echo

echo "Installing Virtualization Tools"
echo
yum install -y kvm qemu-kvm-tools qemu-kvm python-virtinst virt-manager virt-viewer bridge-utils libvirt virt-install
if [ $? != 0 ]; then
	echo "Error: occured duing install of virtualization tools"
	exit
fi
echo "Done installing virtualization tools"
echo

echo "Installing Clustering Tools.."
echo
yum install -y cman corosync rgmanager ricci gfs2-utils ntp lvm2-cluster syslinux gpm
if [ $? != 0 ]; then
	echo "ERROR: occured during install of clustering tools"
	exit
fi
echo "Done installing default clustering tools"
echo

echo "Installing NFS utilities"
echo
yum install -y nfs-utils nfs-utils-lib
if [ $? != 0 ]; then
	echo "Error: occured duing install of nfs utilities"
	exit
fi
echo "Done installing nfs utilities"
echo

echo "Importing ELRepo for DRBD"
echo
rpm --import http://elrepo.org/RPM-GPG-KEY-elrepo.org && rpm -Uvh http://elrepo.org/elrepo-release-6-5.el6.elrepo.noarch.rpm
if [ $? != 0 ]; then
	echo "Error: occured during import of DRBD repo"
	exit
fi
echo "Installing DRBD utilities"
yum install drbd84-utils kmod-drbd84 -y
if [ $? != 0 ]; then
	echo "Error: occured during installation of DRBD utilites"
	exit
fi
echo "Downloading Fencing script"
wget -c http://alteeve.com/files/an-cluster/sbin/obliterate-peer.sh -O /sbin/obliterate-peer.sh
if [ $? != 0 ]; then
	echo "Error: occured during download of fencing script"
	exit
fi
chmod a+x /sbin/obliterate-peer.sh
echo "Done installing DRBD utilites"
echo

echo "Configuring snmpd service"
echo
echo "rocommunity CLOUDTOPT3" >> /etc/snmp/snmpd.conf
if [ $? != 0 ]; then
	echo "Error: occured configuring snmpd"
	exit
fi
echo "Configuring ntpd service"
echo server tick.redhat.com$'\n'restrict tick.redhat.com mask 255.255.255.255 nomodify notrap noquery >> /etc/ntp.conf
if [ $? != 0 ]; then
	echo "Error: occured configuring ntpd"
	exit
fi

echo "Starting required services on start up"
service snmpd start
service ntpd start
chkconfig snmpd on && chkconfig ntpd on
if [ $? != 0 ]; then
	echo "Error: occured starting services on start up"
	exit
fi

echo "Generating SSH keys"
echo
ssh-keygen -t rsa -N "" -b 2048 -f ~/.ssh/id_rsa
if [ $? != 0 ]; then
	echo "Error: occured during generating ssh keys"
	exit
fi
