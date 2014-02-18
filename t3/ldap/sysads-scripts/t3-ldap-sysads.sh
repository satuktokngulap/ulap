#!/bin/bash

TMPPWD=$1

if [ $# -ne 1 ]; then
	echo LDAP PASSWORD required
	exit 0
fi

set -e


cp -f /usr/share/doc/sudo-<version_number>/schema.OpenLDAP /etc/openldap/schema/sudo.schema
restorecon /etc/openldap/schema/sudo.schema

mkdir ~/sudoWork
echo "include /etc/openldap/schema/sudo.schema" > ~/sudoWork/sudoSchema.conf

slapcat -f ~/sudoWork/sudoSchema.conf -F /tmp/ -n0 -s "cn={0}sudo,cn=schema,cn=config" > ~/sudoWork/sudo.ldif

sed -i "s/{0}sudo/sudo/g" ~/sudoWork/sudo.ldif

head -n-8 ~/sudoWork/sudo.ldif > ~/sudoWork/sudo2.ldif

ldapadd -H ldaps:/// -x -D "cn=config" -w $TMPPWD -f ~/sudoWork/sudo2.ldif -v

cat > sudoindexes.ldif << EOF
dn: olcDatabase={3}bdb,cn=config
changetype: modify
add: olcDbIndex
olcDbIndex: sudoUser    eq
olcDbIndex: sudoHost	eq
EOF

ldapadd -H ldaps:/// -x -D "cn=config" -w $TMPPWD -f sudoindexes.ldif -v







