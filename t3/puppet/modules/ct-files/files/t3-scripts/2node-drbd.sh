#!/bin/bash

DRBDADM="/sbin/drbdadm"

$DRBDADM dump
if [ $? -ne 0 ]; then
	echo "Please review configuration files!"
	exit 1;
fi

$DRBDADM create-md r{0..1}
modprobe drbd

$DRBDADM attach r{0..1}
$DRBDADM connect r{0..1}
sleep 5

# Clear bitmap on node sa
MYNAME="`uname -n`"
if [ "$(echo $MYNAME | gawk -F'.' '{print $1}')" = "sa" ]; then
       $DRBDADM -- --clear-bitmap new-current-uuid r{0..1}
fi

service DRBD stop

