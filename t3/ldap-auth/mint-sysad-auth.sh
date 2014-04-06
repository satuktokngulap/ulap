#!/bin/bash
DN=$1
SCHID=$2
TMPPWD=$3


if [ $# -ne 3 ]; then
	
fi

DEBIAN_FRONTEND=noninteractive apt-get install -y libnss-ldap nscd nss-updatedb libnss-db libpam-ccreds sudo-ldap

mv /etc/ldap.conf /etc/ldap.conf.bak
cat > /etc/ldap.conf << EOF
base $DN
uri ldaps://ldap.$SCHID.cloudtop.ph
ldap_version 3
binddn cn=auth,dc=cloudtop,dc=ph
bindpw $TMPPWD
rootbinddn cn=admin,$DN
pam_password md5
ssl on
tls_cacert /etc/ssl/certs/ldap.$SCHID.crt

nss_base_passwd		   ou=users,ou=sysads,dc=cloudtop,dc=ph
nss_base_shadow		   ou=users,ou=sysads,dc=cloudtop,dc=ph
nss_base_group		   ou=roles,ou=sysads,dc=cloudtop,dc=ph

nss_base_passwd		   uid=sysad,o=999 NECTest,st=QC,l=NCR,dc=cloudtop,dc=ph?base
nss_base_shadow 	   uid=sysad,o=999 NECTest,st=QC,l=NCR,dc=cloudtop,dc=ph?base
nss_base_group		   ou=groups,ou=sysads,dc=cloudtop,dc=ph?one


nss_base_passwd        ou=users,$DN?one
nss_base_shadow        ou=users,$DN?one
nss_base_group         ou=roles,$DN?one

sudoers_base ou=sudoroles,ou=sysads,dc=cloudtop,dc=ph
sudoers_debug 5
EOF

mv /etc/ldap/ldap.conf /etc/ldap/ldap.conf.bak
ln -s /etc/ldap.conf /etc/ldap/ldap.conf

mv /etc/pam_ldap.conf /etc/pam_ldap.conf.bak
ln -s  /etc/ldap.conf  /etc/pam_ldap.conf

mv /etc/sudo-ldap.conf /etc/sudo-ldap.conf.bak
ln -s  /etc/ldap.conf  /etc/sudo-ldap.conf

echo $TMPPWD > /etc/ldap.secret

timeout 5 openssl s_client -connect ldap.$SCHID.cloudtop.ph:636 -showcerts > /etc/ssl/certs/ldap.$SCHID.crt

cat > /etc/pam.d/common-auth << EOF
#This configuration enables the use of LDAP and cached creds (ccreds) by PAM.
auth	[success=4 default=ignore]	pam_unix.so nullok_secure
auth	[success=3 default=ignore]	pam_ldap.so use_first_pass
auth	[success=2 default=ignore]	pam_ccreds.so minimum_uid=1000 action=validate use_first_pass
auth	[default=ignore]		pam_ccreds.so minimum_uid=1000 action=update
auth	requisite		pam_deny.so
auth	required			pam_permit.so
auth	optional			pam_ccreds.so minimum_uid=1000 action=store
auth	optional			pam_cap.so
EOF

cat > /etc/pam.d/common-account << EOF
account	[success=2 new_authtok_reqd=done default=ignore]	pam_unix.so
account	[success=1 authinfo_unavail=1 default=ignore]	pam_ldap.so
account	requisite			pam_deny.so
account	required			pam_permit.so
EOF

cat > /etc/pam.d/common-session << EOF
session	[default=1]			pam_permit.so
session	requisite			pam_deny.so
session	required			pam_permit.so
session optional			pam_umask.so
session	required			pam_unix.so
session required	pam_mkhomedir.so skel=/etc/skel/ umask=0077
session	optional			pam_ldap.so
session optional                        pam_ck_connector.so nox11
EOF

cat > /etc/pam.d/common-session-noninteractive << EOF
session	[default=1]			pam_permit.so
session	requisite			pam_deny.so
session	required			pam_permit.so
session optional			pam_umask.so
session	required	pam_unix.so 
session required	pam_mkhomedir.so skel=/etc/skel/ umask=0077
session	optional			pam_ldap.so 
EOF

nss_updatedb ldap

getent passwd

if [ -z $(cat /etc/ssh/sshd_config | grep DenyGroups) ]; then
echo "DenyGroups teachers students"
fi

#reboot
