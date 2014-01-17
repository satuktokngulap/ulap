#!/bin/bash

BASEDN="dc=cloudtop,dc=ph"
PASSWD=$1

echo "This script assumes that the password used is the generic one."
echo "Replace the passwords later."

set -e

HPASSWD=slappasswd -s $PASSWD

if [ $# -ne 1 ];
	then
		echo "PASSWORD REQUIRED"
		exit 0;
fi

cat > root.ldif << EOF
dn: $BASEDN
objectClass: dcObject
objectClass: organization
o: Cloudtop
dc: cloudtop
description: Cloudtop Root Entry

dn: cn=replicator,$BASEDN
objectClass: dcObject
objectClass: simpleSecurityObject
objectClass: organizationalRole
cn: replicator
userPassword: $HPASSWD

dn: cn=auth,$BASEDN
objectClass: dcObject
objectClass: simpleSecurityObject
objectClass: organizationalRole
cn: replicator
userPassword: $HPASSWD

dn: ou=sysads,$BASEDN
objectClass: organizationalUnit
ou: sysads

dn: ou=users,$BASEDN
objectClass: organizationalUnit
ou: users

dn: ou=groups,$BASEDN
objectClass: organizationalUnit
ou: groups

dn: cn=schoolsysad,ou=groups,$BASEDN
objectClass: posixGroup
cn: sysad
gidNumber: 5000
memberUid: sysadm

dn: cn=cloud,ou=groups,$BASEDN
objectClass: posixGroup
cn: cloud
gidNumber: 1000
memberUid: kenan
memberUid: belay
memberUid: gene
memberUid: carlo
memberUid: ken
memberUid: lope
memberUid: gerry

dn: ou=sudoRules,$BASEDN
objectClass: organizationalUnit
ou: sudoRules
description: list of all defined sudo roles

dn: cn=defaults,ou=sudoRoles,$BASEDN
objectClass: sudoRole
cn: defaults
description: default sudoOptions
sudoOption: requiretty
sudoOption: env_reset
sudoOption: env_keep="COLORS DISPLAY HOSTNAME HISTSIZE INPUTRC KDEDIR LS_COLORS"
sudoOption: env_keep+="MAIL PS1 PS2 QTDIR USERNAME LANG LC_ADDRESS LC_CTYPE"
sudoOption: env_keep+="LC_COLLATE LC_IDENTIFICATION LC_MEASUREMENT LC_MESSAGES"
sudoOption: env_keep+="LC_MONETARY LC_NAME LC_NUMERIC LC_PAPER LC_TELEPHONE"
sudoOption: env_keep+="LC_TIME LC_ALL LANGUAGE LINGUAS _XKB_CHARSET XAUTHORITY"
sudoOption: env_keep+=SSH_AUTH_SOCK

dn: cn=%cloud,ou=sudoroles,ou=sysads,$BASEDN
objectClass: top
objectClass: sudoRole
cn: %cloud
description: sudo role definition for the cloud team
sudoCommand: ALL
sudoHost: ALL
sudoUser: %cloud

dn: cn=%sysad,ou=sudoroles,ou=sysads,$BASEDN
objectClass: top
objectClass: sudoRole
cn: %sysad
sudoUser: %sysad
sudoCommand: /bin/cat
sudoCommand: /bin/ls
sudoCommand: /bin/grep
sudoCommand: /usr/bin/tail
sudoCommand: /usr/bin/top
sudoCommand: /usr/bin/virsh
sudoCommand: /bin/ping
sudoCommand: /bin/netstat
sudoCommand: /usr/bin/traceroute
sudoCommand: /sbin/ifconfig
sudoCommand: /usr/sbin/clustat
description: sudo role definition for non-cloud team sysads
sudoHost: ALL
EOF

ldapadd -H ldaps:/// -xD "cn=admin,$BASEDN" -f root.ldif -w $PASSWD

