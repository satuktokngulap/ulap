#!/bin/bash

# Export Proxy
export http_proxy=http://10.225.1.245:8080
export https_proxy=http://10.225.1.245:8080

# Install required packages
rpm -Uvh http://centosrepo.upd.edu.ph/CentOS/upcentos-0.1-1.el6.x86_64.rpm
yum update -y
yum install -y vim rsyslog net-snmp net-snmp-utils net-snmp-devel ntp sudo vixie-cron crontabs kvm qemu-kvm-tools qemu-kvm python-virtinst virt-manager virt-viewer bridge-utils libvirt virt-install cman corosync rgmanager ricci gfs2-utils ntp lvm2-cluster syslinux gpm mlocate rsync wget nfs-utils nfs-utils-lib puppet twisted
chkconfig snmpd on
echo "rocommunity CLOUDTOPT3" >> /etc/snmp/snmpd.conf
service snmpd start
service iptables stop
chkconfig iptables off
echo server tick.redhat.com$'\n'restrict tick.redhat.com mask 255.255.255.255 nomodify notrap noquery >> /etc/ntp.conf
chkconfig ntpd on
service ntpd start
rpm --import http://elrepo.org/RPM-GPG-KEY-elrepo.org
rpm -Uvh http://elrepo.org/elrepo-release-6-5.el6.elrepo.noarch.rpm
yum install drbd84-utils kmod-drbd84 -y
wget -c http://alteeve.com/files/an-cluster/sbin/obliterate-peer.sh -O /sbin/obliterate-peer.sh
chmod a+x /sbin/obliterate-peer.sh
ssh-keygen -t rsa -N "" -b 2048 -f ~/.ssh/id_rsa
rpm -ivh http://yum.puppetlabs.com/el/6/products/x86_64/puppetlabs-release-6-6.noarch.rpm

