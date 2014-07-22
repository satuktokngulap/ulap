#!/bin/bash

# Author: Carlo Santos
# 
#
# This script is the second part of setting-up an LDAP server for Tier 3 
# after a reboot by the first script (t3-server.sh)
# This script does the following:
# - configures rsyslog logging if not yet already done
# - (re)creates a self-signed certificate for the LDAP server
# - adds the password policy and synchronization modules

SCHID=$1
SCHNAME=$2
SCHDIV=$3
SCHREG=$4
TMPPWD=$5

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

if [[ -z $(cat /etc/rsyslog.conf | grep slapd.log) ]]; then
	echo "local4.* 		/var/log/slapd/slapd.log" >> /etc/rsyslog.conf
	service rsyslog restart
fi	


echo "Starting SLAPD"
if [[ -z $(cat /etc/hosts.allow | grep slapd:ALL ) ]]; then 
cat > /etc/hosts.allow << EOF
slapd:ALL
EOF
fi

chcon -t slapd_db_t -R /var/lib/ldap2
slaptest -uv

if pgrep slapd > /dev/null 2>&1
then
	service slapd restart
else
	service slapd start
fi

chkconfig slapd on
sleep 10

set -e

cat > olcAccess1.ldif << EOF
dn: olcDatabase={2}bdb,cn=config
changetype: modify
add: olcAccess
olcAccess: {0}to attrs=employeeType by dn="cn=auth,$DN" read by self read by * none
olcAccess: {1}to attrs=userPassword,shadowLastChange by self write by anonymous auth by * none
olcAccess: {2}to dn.base="" by * none
olcAccess: {3}to * by dn="cn=auth,$DN" read by self write by * none
EOF

echo "Adding OLC access for replication and and referrals"
ldapmodify -xvD "cn=config" -H ldaps:/// -w $TMPPWD -f olcAccess1.ldif

cat > modules.ldif << EOF
dn: cn=module,cn=config
objectClass: olcModuleList
cn: module
olcModulePath: /usr/lib64/openldap
olcModuleLoad: syncprov.la
olcModuleLoad: ppolicy.la
olcModuleLoad: unique.la
EOF

echo "Adding modules for password policy and replication"
ldapadd -xvD "cn=config" -H ldaps:/// -w $TMPPWD -f modules.ldif

cat > overlays.ldif << EOF
dn: olcOverlay=ppolicy,olcDatabase={2}bdb,cn=config
olcOverlay: ppolicy
objectClass: olcOverlayConfig
objectClass: olcPPolicyConfig
olcPPolicyHashCleartext: TRUE
olcPPolicyUseLockout: FALSE
olcPPolicyDefault: cn=default,$DN

dn: olcOverlay=unique,olcDatabase={2}bdb,cn=config
olcOverlay: unique
objectClass: olcOverlayConfig
objectClass: olcUniqueConfig
olcUniqueAttribute: employeeNumber
olcUniqueAttribute: uid
#olcUniqueAttribute: mail
#olcUniqueAttribute: commonName

dn: olcOverlay=unique,olcDatabase={3}bdb,cn=config
olcOverlay: unique
objectClass: olcOverlayConfig
objectClass: olcUniqueConfig
olcUniqueAttribute: employeeNumber
olcUniqueAttribute: uid
#olcUniqueAttribute: mail
#olcUniqueAttribute: commonName

#dn: olcDatabase={2}bdb,cn=config
#changetype: modify
#add: olcMirrorMode
#olcMirrorMode: TRUE

#dn: olcDatabase={3}bdb,cn=config
#changetype: modify
#add: olcMirrorMode
#olcMirrorMode: TRUE
EOF

echo "Creating password policy settings"
ldapadd -xvD "cn=config" -H ldaps:/// -w $TMPPWD -f overlays.ldif

#cat > referral.ldif << EOF
#dn: dc=cloudtop,dc=ph
#objectClass: organization
#objectClass: dcObject
#dc: cloudtop
#o: cloudtop

#dn: l=$SCHREG,dc=cloudtop,dc=ph
#objectClass: locality
#l: $SCHREG

#dn: st=$SCHMUN,l=$SCHREG,dc=cloudtop,dc=ph
#objectClass: locality
#st: $SCHMUN
#l: $SCHREG

#dn: $DN
#objectClass: referral
#objectClass: extensibleObject
#o: $SCHID $SCHNAME
#ref: ldaps://ldap.$SCHID.cloudtop.ph/$DN
#EOF

#ldapadd -xvD "cn=admin,dc=cloudtop,dc=ph" -H ldaps:/// -w $TMPPWD -f referral.ldif
