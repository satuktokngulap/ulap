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
setenforce 1
setsebool -P domain_kernel_load_modules 1

HPWD=$(slappasswd -s $TMPPWD)

cat > /etc/openldap/slapd.d/cn=config/olcDatabase={0}config.ldif << EOF
dn: olcDatabase={0}config
objectClass: olcDatabaseConfig
olcDatabase: {0}config
olcAccess: {0}to *  by dn.base="gidNumber=0+uidNumber=0,cn=peercred,cn=externa
 l,cn=auth" manage  by * none
olcAddContentAcl: TRUE
olcLastMod: TRUE
olcMaxDerefDepth: 15
olcReadOnly: FALSE
olcRootDN: cn=config
olcRootPW: $HPWD
olcSyncUseSubentry: FALSE
olcMonitoring: FALSE
structuralObjectClass: olcDatabaseConfig
EOF

cat > /etc/openldap/slapd.d/cn=config/olcDatabase={2}bdb.ldif << EOF
dn: olcDatabase={2}bdb
objectClass: olcDatabaseConfig
objectClass: olcBdbConfig
olcDatabase: {2}bdb
olcSuffix: $DN
olcAddContentAcl: FALSE
olcLastMod: TRUE
olcMaxDerefDepth: 15
olcReadOnly: FALSE
olcRootDN: cn=admin,$DN
olcRootPW: $HPWD
olcSyncUseSubentry: FALSE
olcMonitoring: TRUE
olcDbDirectory: /var/lib/ldap
olcDbCacheSize: 1000
olcDbCheckpoint: 1024 15
olcDbNoSync: FALSE
olcDbDirtyRead: FALSE
olcDbIDLcacheSize: 0
olcDbIndex: objectClass eq
olcDbIndex: cn eq,sub
olcDbIndex: uid eq,sub
olcDbIndex: uidNumber eq
olcDbIndex: gidNumber eq
olcDbIndex: mail eq
olcDbIndex: ou eq
olcDbIndex: loginShell eq
olcDbIndex: sn eq,sub
olcDbIndex: givenName eq,sub
olcDbIndex: memberUid eq
olcDbIndex: sudoHost pres,eq
olcDbIndex: contextCSN eq
olcDbIndex: entryUUID eq
olcDbLinearIndex: FALSE
olcDbMode: 0600
olcDbSearchStack: 16
olcDbShmKey: 0
olcDbCacheFree: 1
olcDbDNcacheSize: 0
olcDbConfig: set_lg_bsize 10485760
olcDbConfig: set_flags DB_LOG_AUTO_REMOVE
structuralObjectClass: olcBdbConfig
olcAccess: {0}to attrs=employeeType by dn="cn=auth,$DN" read by self read by * none
olcAccess: {1}to attrs=userPassword,shadowLastChange by self write by anonymou
 s auth by * none
olcAccess: {2}to * by dn="cn=auth,$DN"
  read by dn="cn=auth,dc=cloudtop,dc=ph" read by self write by * none
EOF

cat > /etc/openldap/slapd.d/cn=config/olcDatabase={3}bdb.ldif <<EOF
dn: olcDatabase={3}bdb
objectClass: olcDatabaseConfig
objectClass: olcBdbConfig
olcDatabase: {3}bdb
olcSuffix: dc=cloudtop,dc=ph
olcAddContentAcl: FALSE
olcLastMod: TRUE
olcMaxDerefDepth: 15
olcReadOnly: FALSE
olcRootDN: cn=admin,dc=cloudtop,dc=ph
olcRootPW: $HPASSWD
olcSyncUseSubentry: FALSE
olcMonitoring: TRUE
olcDbDirectory: /var/lib/ldap2
olcDbCacheSize: 1000
olcDbCheckpoint: 1024 15
olcDbNoSync: FALSE
olcDbDirtyRead: FALSE
olcDbIDLcacheSize: 0
olcDbIndex: objectClass eq
olcDbIndex: cn eq,sub
olcDbIndex: uid eq,sub
olcDbIndex: uidNumber eq
olcDbIndex: gidNumber eq
olcDbIndex: mail eq
olcDbIndex: ou eq
olcDbIndex: loginShell eq
olcDbIndex: sn eq,sub
olcDbIndex: givenName eq,sub
olcDbIndex: memberUid eq,sub
olcDbIndex: sudoHost eq
olcDbIndex: sudoUser eq
olcDbIndex: contextCSN eq
olcDbIndex: entryUUID eq
olcDbLinearIndex: FALSE
olcDbMode: 0600
olcDbSearchStack: 16
olcDbShmKey: 0
olcDbCacheFree: 1
olcDbDNcacheSize: 0
olcDbConfig: set_lg_bsize 10485760
olcDbConfig: set_flags DB_LOG_AUTO_REMOVE
structuralObjectClass: olcBdbConfig
olcAccess: {0}to attrs=userPassword,shadowLastChange by self read by anonymous
  auth by * none
olcAccess: {1}to * by dn="cn=auth,dc=cloudtop,dc=ph" read by self read by * no
 ne
olcAccess: {2}to dn.base="$DN" by dn="cn=auth,$DN" read by dn="cn=dataadmin,$DN" write
EOF

chown -R ldap:ldap /etc/openldap/slapd.d/
