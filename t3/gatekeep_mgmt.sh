#!/bin/bash

#Function for checking mgmt
chkname(){
	SCHID=$1
	echo -n "Checking if host name is in the proper format..."
	if [[ "$(hostname)" = "ldap.$SCHID.cloudtop.ph" ]]; then
		echo_success
		echo
		return 0
	else
		echo_failure
		echo
		return 1
	fi
}

#Function for checking if SSL certificate is present
chksslcert(){
	echo -n "Checking if SSL certificate exists..."
	if [ -z $(certutil -L -d /etc/openldap/certs) | grep "OpenLDAP Server") ]; then
		echo "No certificate file found"
		return 1
	else
		echo "Certificate exists"
		return 0
	fi
}

#Function for checking if SSL cert can be retrieved over the network
chkssl(){
	SCHID=$1
	echo -n "Checking if openssl connection to this VM works..."
	timeout 5 openssl s_client -connect ldap.$SCHID.cloudtop.ph:636 &> out
	ERR=$(cat out | grep err | grep -v "self signed certificate")
	if [ -z $ERR ]; then
		echo_success
		echo "No errors found but certificate must be replaced if self-signed."
		return 0
	else
		echo_failure
		echo $ERR
		return 1
	fi
}

chkschooladminaccess(){
	
}


