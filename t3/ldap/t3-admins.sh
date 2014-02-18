#!/bin/bash

BASEDN=$1
PASSWD=$2

HPASSWD=$(slappasswd -s $PASSWD)

cat > schooladmins.ldif << EOF
dn: uid=sysad,$BASEDN
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

dn: cn=dataadmin,$BASEDN
objectClass: organizationalRole
objectClass: simpleSecurityObject
cn: dataadmin
description: data administrator for this setup
userpassword: $HPASSWD
EOF

ldapadd -xD "cn=admin,$BASEDN" -w $PASSWD -H ldaps:/// -f schooladmins.ldif
