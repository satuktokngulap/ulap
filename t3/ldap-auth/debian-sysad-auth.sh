#!/bin/bash
DN=$1
SCHID=$2
TMPPWD=$3


if [ $# -ne 3 ]; then
	echo "The number of arguments passed is not equal to 3."
fi

DEBIAN_FRONTEND=noninteractive apt-get install -y libnss-ldap nscd nss-updatedb libnss-db libpam-ccreds nss-pam-ldapd

cat > /etc/cron.hourly/nssupdate.sh << EOF
#!/bin/sh
nss_updatedb ldap
exit 0
EOF

chmod +x /etc/cron.hourly/nssupdate.sh

sed -i "s/passwd:.*$/passwd: compat ldap/g" /etc/nsswitch.conf
sed -i "s/group:.*$/group: compat ldap/g" /etc/nsswitch.conf
sed -i "s/shadow:.*$/shadow: compat ldap/g" /etc/nsswitch.conf


if [ -z $(cat /etc/nsswitch.conf | grep sudoers ) ]; then
	echo "sudoers: files ldap" >> /etc/nsswitch.conf
else
	sed -i "s/sudoers:*$/sudoers: files ldap/g" /etc/nsswitch.conf
fi

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





