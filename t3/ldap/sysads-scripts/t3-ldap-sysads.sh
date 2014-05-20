#!/bin/bash

SCHID=$1
SCHNAME=$2
SCHMUN=$3
SCHREG=$4
TMPPWD=$5

if [ $# -ne 1 ]; then
	echo LDAP PASSWORD required
	exit 0
fi

set -e

DN="o=$SCHID $SCHNAME,st=$SCHMUN,l=$SCHREG,dc=cloudtop,dc=ph"

SCHEMA=$(locate schema.OpenLDAP | grep sudo)

cp -f $SCHEMA /etc/openldap/schema/sudo.schema
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

cat > access.ldif << EOF
dn: olcDatabase={3}bdb,cn=config
changetype: modify
replace: olcAccess
olcAccess: {0}to attrs=userPassword,shadowLastChange by self read by anonymous auth by * none
olcAccess: {1}to * by dn="cn=auth,dc=cloudtop,dc=ph" read by self read by * none
olcAccess: {2}to dn.base="$DN" by dn="cn=auth,$DN" read by dn="cn=dataadmin,$DN" write
olcAccess: {3}to dn.base="" by * none
#olcAccess: {1}to * by dn="cn=auth,dc=cloudtop,dc=ph" read by self read by * none
#olcAccess: {2}to dn.base="$DN" by dn="cn=$DN" read by dn="cn=dataadmin,$DN" write
EOF

ldapadd -H ldaps:/// -x -D "cn=config" -w $TMPPWD -f access.ldif -v

echo "Adding the LDAP referral from the sysad tree to the client tree"

service slapd stop
mv /etc/openldap/slapd.d/cn=config/olcDatabase{2}bdb.ldif /etc/openldap/slapd.d/cn=config/olcDatabase{2}bdb.ldif.bak
service slapd start

cat > referral.ldif << EOF
dn: $DN
objectClass: referral
objectClass: extensibleObject
o: $SCHID $SCHNAME
ref: ldaps://ldap.$SCHID.cloudtop.ph/$DN
EOF

ldapadd -xvD "cn=admin,dc=cloudtop,dc=ph" -H ldaps:/// -w $TMPPWD -f referral.ldif

service slapd stop
mv /etc/openldap/slapd.d/cn=config/olcDatabase{2}bdb.ldif.bak /etc/openldap/slapd.d/cn=config/olcDatabase{2}bdb.ldif
service slapd start
