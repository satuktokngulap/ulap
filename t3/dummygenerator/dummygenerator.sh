#!/bin/bash

SCHID=$1
SCHNAME=$2
SCHDIV=$3
SCHREG=$4
DUMMYCOUNT=$5

if [ $# -ne 5 ]; then
	echo "Wrong number of arguments passed. 5 Required. Got $#"
	exit
fi

LDIFOUT="dummyAccs-$SCHID.ldif"

touch $LDIFOUT

STUDENTHPWD=$(slappasswd -s student)

for (( i=1; i<=$DUMMYCOUNT; i++ ))
do
cat >> ${LDIFOUT} << EOF 
dn: uid=student$i,ou=users,o=$SCHID $SCHNAME,st=$SCHDIV,l=$SCHREG,dc=cloudtop,dc=ph
objectClass: posixAccount
objectClass: shadowAccount
objectClass: inetOrgPerson
cn: student$i
uid: student$i
uidNumber: ${SCHID}${i}
loginShell: /bin/bash
homeDirectory: /home/nfs/student${i}
gidNumber: ${SCHID}1${i}
userPassword: $STUDENTHPWD
givenName: given name ${i}
mail: NA
homePostalAddress: NA
homeTelephoneNumber: NA
mobileTelephoneNumber: NA
sn: student${i}

EOF
done

TEACHERHPWD=$(slappasswd -s teacher)

for (( i=1; i<=$DUMMYCOUNT; i++ ))
do
cat >> ${LDIFOUT} << EOF 
dn: uid=teacher$i,ou=users,o=$SCHID $SCHNAME,st=$SCHDIV,l=$SCHREG,dc=cloudtop,dc=ph
objectClass: posixAccount
objectClass: shadowAccount
objectClass: inetOrgPerson
cn: teacher$i
uid: teacher$i
uidNumber: ${SCHID}${i}
loginShell: /bin/bash
homeDirectory: /home/nfs/teacher${i}
gidNumber: ${SCHID}1${i}
userPassword: $TEACHERHPWD
givenName: teacher given name ${i}
mail: NA
homePostalAddress: NA
homeTelephoneNumber: NA
mobileTelephoneNumber: NA
sn: teacher${i}

EOF
done

cat >> ${LDIFOUT} << EOF
dn: cn=teachers,o=$SCHID $SCHNAME,st=$SCHDIV,l=$SCHREG,dc=cloudtop,dc=ph
objectClass: posixGroup
cn: teachers
gidNumber: ${SCHID}2
EOF

for (( i=1; i<=$DUMMYCOUNT; i++ ))
do
cat >> ${LDIFOUT} << EOF 
memberuid: teacher${i}
EOF
done
echo "" >> ${LDIFOUT}

cat >> ${LDIFOUT} << EOF
dn: cn=students,o=$SCHID $SCHNAME,st=$SCHDIV,l=$SCHREG,dc=cloudtop,dc=ph
objectClass: posixGroup
cn: students
gidNumber: ${SCHID}1
EOF

for (( i=1; i<=$DUMMYCOUNT; i++ ))
do
cat >> ${LDIFOUT} << EOF 
memberuid: student${i}
EOF
done

cat ${LDIFOUT}
