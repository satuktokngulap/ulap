#!/bin/bash

RED=$(tput setaf 1)
GREEN=$(tput setaf 2)
NORMAL=$(tput sgr0)
COL=80

SCHOOLID=$1
USERLISTFILE=$2

echo_success(){
	#echo -e $i "[\033[60G\033[31m[ FAILED \033[0m]"
	echo -e "\033[80G[$GREEN OK $NORMAL]"
	return $TRUE
}

echo_failure(){
	echo -e "\033[80G[$RED FAIL $NORMAL]"
	return $TRUE
}

check_nssupdate(){
	OUT=$(nss_updatedb ldap)
	
	echo -ne $OUT
	if [[ $OUT == "passwd... done.*" ]] && [[ $OUT == "*group... done*" ]]; then
		echo_success
	else
		echo_failure
	fi
}

check_getent(){
	
	for i in {1..40}
	do
		ret=false
		getent passwd teacher$i > /dev/null 2>&1 && ret=true
		
		if $ret; then
			echo "user teacher$i present..."
		else
			echo "user teacher$i absent..."
			return 1
		fi
	done
	
	for i in {1..40}
	do
		ret=false
		getent passwd student$i > /dev/null 2>&1 && ret=true
		
		if $ret; then
			echo "user student$i present..."
		else
			echo "user student$i absent..."
			return 1
		fi
	done
	
	return 0
}

RESULT=check_getent

if $RESULT; then
	echo "Test success"
else
	echo "Test failed"
fi

