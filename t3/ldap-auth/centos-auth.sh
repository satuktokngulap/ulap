#!/bin/bash


#This script is for the LDAP server itself.
SCHID=$1
PASSWD=$2

DN="dc=cloudtop,dc=ph"

yum install -y pam_ldap sssd libsss_sudo

authconfig --enablesssd --enablesssdauth --enablecachecreds --enableldap \
    --enableldaptls --enableldapauth --ldapserver=ldap.$SCHID.cloudtop.ph --ldapbasedn="$BASEDN" \
    --disablenis --disablekrb5 --enableshadow --enablemkhomedir \
    --enablelocauthorize --updateall

cat > /etc/sssd/sssd.conf << EOF
[domain/default]
debug_level = 5
ldap_id_use_start_tls = True
cache_credentials = True
ldap_search_base = dc=cloudtop,dc=ph
ldap_user_search_base = dc=cloudtop,dc=ph
ldap_group_search_base = dc=cloudtop,dc=ph
ldap_sudo_search_base = ou=sudoroles,ou=sysads,dc=cloudtop,dc=ph
id_provider = ldap
auth_provider = ldap
access_provider = ldap
ldap_uri = ldaps://ldap.$SCHID.cloudtop.ph
ldap_tls_cacertdir = /etc/openldap/certs
ldap_default_bind_dn = cn=auth,dc=cloudtop,dc=ph
ldap_default_authtok_type = password
ldap_default_authtok = $TMPPWD
ldap_access_filter = employeeType=sysad
enumerate = True

[sssd]
services = nss, pam, sudo, ssh

[ssh]
EOF

timeout 3 openssl s_client -connect ldap.$SCHID.cloudtop.ph:636 -showcerts >> /etc/openldap/certs/ldap.crt

cat > /etc/ldap.conf << EOF
tls_cacertdir /etc/openldap/certs
pam_password md5
uri ldaps://ldap.$SCHID.cloudtop.ph
base dc=cloudtop,dc=ph
binddn cn=auth,dc=cloudtop,dc=ph
bindpw $TMPPWD
ssl on
sudoers_base ou=sudoroles,ou=sysads,dc=cloudtop,dc=ph
sudoers_debug 5
EOF

mv /etc/openldap/ldap.conf /etc/openldap/ldap.conf.bak
ln -s  /etc/ldap.conf  /etc/openldap/ldap.conf

mv /etc/pam_ldap.conf /etc/pam_ldap.conf.bak
ln -s  /etc/ldap.conf  /etc/pam_ldap.conf

mv /etc/sudo-ldap.conf /etc/sudo-ldap.conf.bak
ln -s  /etc/ldap.conf  /etc/sudo-ldap.conf

NSSSUDO=cat /etc/nsswitch.conf | grep sudoers

if [ -z $NSSSUDO ]; then
echo "sudoers:    sss ldap" >> /etc/nsswitch.conf
fi

service sssd restart


