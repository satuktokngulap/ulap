#!/bin/bash

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

hostname $TMPHNAME;
hostname

ADDR=$(ifconfig eth0 | grep inet | grep -v inet6 |  awk '{print $2}')
IP=${ADDR#"addr:"}
HOSTENT=$(cat /etc/hosts | grep "$TMPHNAME")

sed -i "s/HOSTNAME=.*/HOSTNAME=$TMPHNAME/g" /etc/sysconfig/network

cat /etc/sysconfig/network

service network restart

if [ -z "$HOSTENT" ] 
then
	echo "$IP $TMPHNAME" >> /etc/hosts
else
	sed -i "s/^.*$TMPHNAME$/$IP $TMPHNAME/g" /etc/hosts
fi

cat /etc/hosts

echo "Updated hostname and /etc/hosts. To make changes permanent, rebooting must be done."

#echo "IP: $IP"

echo "Updating access control lists for LDAP for clients"

sed -i "s/^.*olcAccess: {0}.*/olcAccess: {0}to dn.base="" attrs=namingContexts by * none/g" /etc/openldap/slapd.d/cn=config/olcDatabase={2}bdb.ldif
sed -i "s/^.*olcAccess: {1}.*/olcAccess: {1}to * by dn=\"cn=replicator,$DN\" read by * none/g " /etc/openldap/slapd.d/cn=config/olcDatabase={2}bdb.ldif
sed -i "s/^.*olcAccess: {2}.*/olcAccess: {2}to dn.one=\"uid=,ou=users,$DN\" by self read by * none/g" /etc/openldap/slapd.d/cn=config/olcDatabase={2}bdb.ldif
sed -i "s/^.*olcAccess: {3}.*/olcAccess: {3}to dn.subtree=\"ou=users,$DN\" by dn.one=\"uid=dataadmin,ou=users,$DN\" write by * none/g" /etc/openldap/slapd.d/cn=config/olcDatabase={2}bdb.ldif
sed -i "/^.*olcAccess: {3}.*/a olcAccess: {4}to attrs=userPassword,shadowLastChange by self read by anonymous auth by * none" /etc/openldap/slapd.d/cn=config/olcDatabase={2}bdb.ldif
sed -i "/^.*olcAccess: {4}.*/a olcAccess: {5}to * by dn=\"cn=auth,dc=cloudtop,dc=ph\" read by self read by * none" /etc/openldap/slapd.d/cn=config/olcDatabase={2}bdb.ldif

cat /etc/openldap/slapd.d/cn=config/olcDatabase={2}bdb.ldif | grep olcAccess
echo "Updated access control lists for LDAP for clients"

echo "Updating Base DN, root DN, and passwords"

sed -i "s/olcRootDN: .*/olcRootDN: cn=admin,$DN/g" /etc/openldap/slapd.d/cn=config/olcDatabase={2}bdb.ldif
sed -i "s/olcSuffix: .*/olcSuffix: $DN/g" /etc/openldap/slapd.d/cn=config/olcDatabase={2}bdb.ldif

HPWD=$(slappasswd -s $TMPPWD)

echo $HPWD
sed -i "/olcRootDN.*/a olcRootPW: $HPWD" /etc/openldap/slapd.d/cn=config/olcDatabase={0}config.ldif
sed -i "/olcRootDN.*/a olcRootPW: $HPWD" /etc/openldap/slapd.d/cn=config/olcDatabase={2}bdb.ldif
sed -i "/olcRootDN.*/a olcRootPW: $HPWD" /etc/openldap/slapd.d/cn=config/olcDatabase={3}bdb.ldif

cat /etc/openldap/slapd.d/cn=config/olcDatabase={0}config.ldif | grep olcRootPW
cat /etc/openldap/slapd.d/cn=config/olcDatabase={2}bdb.ldif | grep olcRootPW
cat /etc/openldap/slapd.d/cn=config/olcDatabase={3}bdb.ldif | grep olcRootPW

echo "Updated Base DN, root DN, and passwords"
