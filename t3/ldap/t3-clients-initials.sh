#!/bin/bash

# Author: Carlo Santos
# 
#
# This script is the third part of setting-up an LDAP server for Tier 3 
# after t3-server1.sh.
# This script does the following:
# - Adds the initial entries for the LDAP server for clients
# - Adds default password policy for clients
# - Creates local administration accounts, one for the system and one for data


SCHID=$1
SCHNAME=$2
SCHDIV=$3
SCHREG=$4
TMPPWD=$5
SCHMUN=$6
SCHDIST=$7
PROVID=$8

DN="o=$SCHID $SCHNAME,st=$SCHDIV,l=$SCHREG,dc=cloudtop,dc=ph"

if [ $# -lt 5 ];
	then
		echo "Some parameters missing."
		echo "Parameters are expected to be in the following order:"
		echo "    <school ID (based on DepEd spreadsheet)>"
		echo "    <school name (based on DepEd spreadsheet)>"
		echo "    <municipality of the school>"
		echo "    <region of the school>"
		echo "    <TEMPORARY password to be used>"
		echo ""
		echo "Optional parameters are expected in the following order:"
		echo "    <school division name (based on the DepEd spreadsheet)>"
		echo "    <school district name (based on the DepEd spreadsheet)>"
		echo "    <provincial ID (based on the DepEd spreadsheet)>"
		exit 0;
fi

cat > root.ldif << EOF
dn: $DN
objectClass: organization
o: $SCHID $SCHNAME
st: $SCHDIV
l: $SCHREG
description: SchDivName=$6,SchDivDist=$7,ProvID=$8
EOF

ldapadd -H ldaps:/// -xD "cn=admin,$DN" -f root.ldif -w $TMPPWD -cv

HPASSWD=$(slappasswd -s $TMPPWD)

cat > initials.ldif << EOF
dn: cn=auth,$DN
objectClass: simpleSecurityObject
objectClass: organizationalRole
cn: auth
description: Account for auth
userPassword: $HPASSWD

dn: cn=replicator,$DN
objectClass: simpleSecurityObject
objectClass: organizationalRole
cn: replicator
description: Account for replication
userPassword: $HPASSWD

dn: ou=users,$DN
objectClass: organizationalUnit
ou: users
st: $SCHMUN
l: $SCHREG

dn: ou=roles,$DN
objectClass: organizationalUnit
ou: roles
st: $SCHMUN
l: $SCHREG
EOF

ldapadd -H ldaps:/// -xD "cn=admin,$DN" -f initials.ldif -w $TMPPWD -cv

cat > ppolicy.ldif <<EOF
dn: ou=pwpolicies,$DN
objectClass: organizationalUnit
objectClass: top
ou: pwpolicies

dn: cn=default,ou=pwpolicies,$DN
cn: default
objectClass: pwdPolicy
objectClass: person
objectClass: top
pwdAllowUserChange: TRUE
pwdAttribute: 2.5.4.35
pwdExpireWarning: 2592000
pwdFailureCountInterval: 30
pwdGraceAuthNLimit: 0
pwdInHistory: 10
pwdLockout: TRUE
pwdLockoutDuration: 3600
pwdMaxAge: 31536000
pwdMaxFailure: 5
pwdMinAge: 3600
pwdMinLength: 6
pwdMustChange: FALSE
pwdSafeModify: FALSE
sn: dummy value
EOF

echo "Adding password policy for clients"
ldapadd -xvD "cn=admin,$DN" -H ldaps:/// -w $TMPPWD -f ppolicy.ldif

cat > schooladmins.ldif << EOF
dn: uid=sysad,ou=users,$DN
objectClass: inetOrgPerson
objectClass: posixAccount
objectClass: shadowAccount
uid: sysad
cn: sysad
sn: sysad
uidNumber: 5000
loginShell: /bin/bash
homeDirectory: /home/sysad
gidNumber: 5000
userPassword: $HPASSWD
employeeType: sysad

dn: cn=dataadmin,ou=users,$DN
objectClass: organizationalRole
objectClass: simpleSecurityObject
cn: dataadmin
description: data administrator for this setup
userpassword: $HPASSWD
EOF

ldapadd -xvD "cn=admin,$DN" -w $TMPPWD -H ldaps:/// -f schooladmins.ldif

