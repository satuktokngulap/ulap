#!/bin/bash

# This script is the fourth part of setting-up an LDAP server for Tier 3 
# after t3-clients-initials.sh.
# This script adds the following to the LDAP server:
# - LDAP initial entry for sysads
# - sudo access definitions
# - cloud team sysad accounts

BASEDN="dc=cloudtop,dc=ph"
PASSWD=$1

echo "This script assumes that the password used is the generic one."
echo "Replace the passwords later."

set -e

HPASSWD=$(slappasswd -s $PASSWD)

if [ $# -ne 1 ];
	then
		echo "PASSWORD REQUIRED"
		exit 0;
fi

if pgrep slapd > /dev/null 2>&1
then
	service slapd stop
fi

cat > root.ldif << EOF
dn: $BASEDN
objectClass: dcObject
objectClass: organization
o: Cloudtop
dc: cloudtop
description: Cloudtop Root Entry

dn: cn=replicator,$BASEDN
objectClass: simpleSecurityObject
objectClass: organizationalRole
cn: replicator
userPassword: $HPASSWD

dn: cn=auth,$BASEDN
objectClass: dcObject
objectClass: simpleSecurityObject
objectClass: organizationalRole
cn: auth
dc: cloudtop
userPassword: $HPASSWD

dn: ou=sysads,$BASEDN
objectClass: organizationalUnit
ou: sysads

dn: ou=users,ou=sysads,$BASEDN
objectClass: organizationalUnit
ou: users

dn: ou=groups,ou=sysads,$BASEDN
objectClass: organizationalUnit
ou: groups

dn: cn=sysad,ou=groups,ou=sysads,$BASEDN
objectClass: posixGroup
cn: sysad
gidNumber: 5000
memberUid: sysad

#dn: cn=ctel,ou=groups,ou=sysads,$BASEDN
#objectClass: posixGroup
#cn: ctel
#gidNumber: 5001
#memberUid: ctel

dn: cn=cloud,ou=groups,ou=sysads,$BASEDN
objectClass: posixGroup
cn: cloud
gidNumber: 2001
memberUid: kenan
memberUid: belay
memberUid: gene
memberUid: carlo
memberUid: ken
memberUid: lope
memberUid: gerry

dn: ou=sudoroles,ou=sysads,$BASEDN
objectClass: organizationalUnit
ou: sudoroles
description: list of all defined sudo roles

dn: cn=defaults,ou=sudoroles,ou=sysads,$BASEDN
objectClass: sudorole
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

dn: cn=ctel,ou=sudoroles,ou=sysads,$BASEDN
objectClass: top
objectClass: sudoRole
cn: elearning
description: sudo role definition for elearning
sudoCommand: ALL
sudoHost: ALL
sudoUser: ctel

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

ldapadd -H ldaps:/// -xD "cn=admin,$BASEDN" -f root.ldif -w $PASSWD -v

cat > ctel.ldif << EOF
dn: uid=ctel,ou=users,ou=sysads,dc=cloudtop,dc=ph
objectClass: inetOrgPerson
objectClass: posixAccount
objectClass: shadowAccount
uid: ctel
sn: ctel
cn: ctel
uidNumber: 5001
loginShell: /bin/bash
homeDirectory: /home/ctel
gidNumber: 5001
userPassword: $HPASSWD
employeeType: ctel
EOF

#ldapadd -H ldaps:/// -xD "cn=admin,$BASEDN" -f ctel.ldif -w $PASSWD -v

## insert cloud team account creation here
cat > cloud.ldif << EOF
dn: uid=belay,ou=users,ou=sysads,dc=cloudtop,dc=ph
objectClass: inetOrgPerson
objectClass: posixAccount
objectClass: shadowAccount
uid: belay
sn: montes
cn: belay montes
uidNumber: 2001
loginShell: /bin/bash
homeDirectory: /home/belay
gidNumber: 2001
userPassword: $HPASSWD
employeeType: sysad

dn: uid=carlo,ou=users,ou=sysads,dc=cloudtop,dc=ph
objectClass: inetOrgPerson
objectClass: posixAccount
objectClass: shadowAccount
uid: carlo
sn: santos
cn: carlo santos
uidNumber: 1002
loginShell: /bin/bash
homeDirectory: /home/carlo
gidNumber: 2001
userPassword: $HPASSWD
employeeType: sysad

dn: uid=gene,ou=users,ou=sysads,dc=cloudtop,dc=ph
objectClass: inetOrgPerson
objectClass: posixAccount
objectClass: shadowAccount
uid: gene
sn: quevedo
cn: gene quevedo
uidNumber: 1003
loginShell: /bin/bash
homeDirectory: /home/gene
gidNumber: 2001
userPassword: $HPASSWD
employeeType: sysad

dn: uid=gerry,ou=users,ou=sysads,dc=cloudtop,dc=ph
objectClass: inetOrgPerson
objectClass: posixAccount
objectClass: shadowAccount
uid: gerry
sn: roxas
cn: gerry roxas
uidNumber: 1004
loginShell: /bin/bash
homeDirectory: /home/gerry
gidNumber: 2001
userPassword: $HPASSWD
employeeType: sysad

dn: uid=ken,ou=users,ou=sysads,dc=cloudtop,dc=ph
objectClass: inetOrgPerson
objectClass: posixAccount
objectClass: shadowAccount
uid: ken
sn: salanio
cn: ken salanio
uidNumber: 1005
loginShell: /bin/bash
homeDirectory: /home/ken
gidNumber: 2001
userPassword: $HPASSWD
employeeType: sysad

dn: uid=kenan,ou=users,ou=sysads,dc=cloudtop,dc=ph
objectClass: inetOrgPerson
objectClass: posixAccount
objectClass: shadowAccount
uid: kenan
sn: virtucio
cn: kenan virtucio
uidNumber: 1006
loginShell: /bin/bash
homeDirectory: /home/kenan
gidNumber: 2001
userPassword: $HPASSWD
employeeType: sysad

dn: uid=lope,ou=users,ou=sysads,dc=cloudtop,dc=ph
objectClass: inetOrgPerson
objectClass: posixAccount
objectClass: shadowAccount
uid: lope
sn: beltran
cn: lope beltran
uidNumber: 1007
loginShell: /bin/bash
homeDirectory: /home/lope
gidNumber: 2001
userPassword: $HPASSWD
employeeType: sysad
EOF

ldapadd -H ldaps:/// -xD "cn=admin,$BASEDN" -f cloud.ldif -w $PASSWD -v