#!/bin/bash

# Author: Carlo Santos
# 
#
# This script is the second part of setting-up an LDAP server for Tier 3 
# after a reboot by the first script (t3-server.sh)
# This script does the following:
# - Creates/replaces the SSL certificate of the LDAP server
# - Updates rsyslog to include slapd logging
# - Updates hosts.allow to allow all for slapd
# - Checks configuration via slaptest and enables slapd
# - Adds password policy and replication modules
# - Adds password policy configuration to LDAP
# - Creates a referral object that points from LDAP B (sysads) to LDAP A (clients) 

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

echo "Creating temporary self-signed certificate"
CERT=$(certutil -L -d /etc/openldap/certs | grep "OpenLDAP Server"| awk '{print $1}')
if [ -z $CERT ]
	then
		echo "Cert is absent, creating self-signed cert. Replace ASAP"
	else
		echo "Cert is present. Replacing with another one"
		certutil -D -d /etc/openldap/certs -n "OpenLDAP Server"
		
fi
/usr/libexec/openldap/create-certdb.sh
/usr/libexec/openldap/generate-server-cert.sh


echo "Created temporary self-signed certificate"

echo "Fix logging"

if [ -z $(cat /etc/rsyslog.conf | grep slapd.log) ]
	then
	
	cat >> /etc/rsyslog.conf << EOF
	local4.* 					/var/log/slapd/slapd.log		
	EOF
	
	service rsyslog restart
fi


echo "Starting SLAPD"
cat > /etc/hosts.allow << EOF
slapd:ALL
EOF

slaptest -uv
service slapd start
chkconfig slapd on

echo "Adding the password policy and replication modules"

cat > modules.ldif << EOF
dn: cn=module,cn=config
objectClass: olcModuleList
cn: module
olcModulePath: /usr/lib64/openldap
olcModuleLoad: syncprov.la
olcModuleLoad: ppolicy.la
EOF

ldapadd -xvD "cn=config" -H ldaps:/// -w $TMPPWD -f modules.ldif

cat > overlays.ldif << EOF
dn: olcOverlay=ppolicy,olcDatabase={2}bdb.ldif,cn=config
olcOverlay: ppolicy
objectClass: olcOverlayConfig
objectClass: olcPPolicyConfig
olcPPolicyHashCleartext: TRUE
olcPPolicyUseLockout: FALSE
olcPPolicyDefault: cn=default,$DN

#dn: olcDatabase={2}bdb,cn=config
#changetype: modify
#add: olcMirrorMode
#olcMirrorMode: TRUE

#dn: olcDatabase={3}bdb,cn=config
#changetype: modify
#add: olcMirrorMode
#olcMirrorMode: TRUE
EOF

ldapadd -xvD "cn=config" -H ldaps:/// -w $TMPPWD -f overlays.ldif

cat > referral.ldif << EOF
dn: l=$SCHREG,dc=cloudtop,dc=ph
objectClass: locality
l: $SCHREG

dn: st=$SCHMUN,l=$SCHREG,dc=cloudtop,dc=ph
objectClass: locality
st: $SCHMUN
l: $SCHREG

dn: $DN
objectClass: referral
objectClass: extensibleObject
o: $SCHID $SCHNAME
ref: ldaps://ldap.$SCHID.cloudtop.ph/$DN
EOF

ldapadd -xvD "cn=config" -H ldaps:/// -w $TMPPWD -f overlays.ldif
