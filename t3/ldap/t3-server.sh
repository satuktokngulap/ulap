#!/bin/bash

# Author: Carlo Santos
# 
#
# This script is the first part of setting-up an LDAP server for Tier 3.
# This script does the following:
# - Enable SELINUX
# - Update the host name
# - Update LDAP Root DNs
# - Update LDAP Root Passwords
# - Update LDAP Suffix
# - Reboots VM to make changes to hostname permanent
#
# Note: This LDAP server setup hols 2 LDAP trees

SCHID=$1
SCHNAME=$2
SCHMUN=$3
SCHREG=$4
TMPPWD=$5

#set -e

if [ $# -ne 5 ];
	then
		echo "Some parameters missing."
		echo "Parameters are expected to be in the following order:"
		echo "<school ID (based on DepEd spreadsheet)>"
		echo "<school name (based on DepEd spreadsheet)>"
		echo "<municipality of the school>"
		echo "<region of the school>"
		echo "<TEMPORARY password to be used>"
		exit 0;
fi

DN="o=$1 $2,st=$3,l=$4,dc=cloudtop,dc=ph"

echo "This LDAP server is for users in $DN"

echo "activating SELinux"
#if [ getenforce -ne 1 ];
#	then
		setenforce 1
		setsebool -P domain_kernel_load_modules 1
#fi

echo "Updating the hostname and /etc/hosts"
TMPHNAME="ldap.$SCHID.cloudtop.ph"

#hostname $TMPHNAME;
hostname

#ADDR=$(ifconfig eth0 | grep inet | grep -v inet6 |  awk '{print $2}')
#IP=${ADDR#"addr:"}
#HOSTENT=$(cat /etc/hosts | grep "$TMPHNAME")

#sed -i "s/HOSTNAME=.*/HOSTNAME=$TMPHNAME/g" /etc/sysconfig/network

#cat /etc/sysconfig/network

#service network restart

#if [ -z "$HOSTENT" ] 
#then
#	echo "$IP $TMPHNAME" >> /etc/hosts
#else
#	sed -i "s/^.*$TMPHNAME$/$IP $TMPHNAME/g" /etc/hosts
#fi

cat /etc/hosts

#echo "Updated hostname and /etc/hosts. To make changes permanent, rebooting must be done."

#echo "IP: $IP"

echo "Updating Base DN, root DN, and passwords"

sed -i "s/olcRootDN: .*/olcRootDN: cn=admin,$DN/g" /etc/openldap/slapd.d/cn=config/olcDatabase={2}bdb.ldif
sed -i "s/olcSuffix: .*/olcSuffix: $DN/g" /etc/openldap/slapd.d/cn=config/olcDatabase={2}bdb.ldif

HPWD=$(slappasswd -s $TMPPWD)

echo $HPWD
sed -i "/olcRootDN.*$/a olcRootPW: $HPWD" /etc/openldap/slapd.d/cn=config/olcDatabase={0}config.ldif
sed -i "/olcRootDN.*$/a olcRootPW: $HPWD" /etc/openldap/slapd.d/cn=config/olcDatabase={2}bdb.ldif
sed -i "/olcRootDN.*$/a olcRootPW: $HPWD" /etc/openldap/slapd.d/cn=config/olcDatabase={3}bdb.ldif

cat /etc/openldap/slapd.d/cn=config/olcDatabase={0}config.ldif | grep olcRootPW
cat /etc/openldap/slapd.d/cn=config/olcDatabase={2}bdb.ldif | grep olcRootPW
cat /etc/openldap/slapd.d/cn=config/olcDatabase={3}bdb.ldif | grep olcRootPW

echo "Updated Base DN, root DN, and passwords"

#reboot
