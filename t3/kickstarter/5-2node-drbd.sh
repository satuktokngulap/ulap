#!/bin/bash

DRBDADM="/sbin/drbdadm"

$DRBDADM dump
if [ $? -ne 0 ]; then
	echo "Please review configuration files!"
	exit 1;
fi

$DRBDADM create-md r{0..1}
modprobe drbd

$DRBDADM up r{0..1}

# Clear bitmap on node sa
MYNAME="`uname -n`"
if [ "$(echo $MYNAME | gawk -F'.' '{print $1}')" = "sa" ]; then
	$DRBDADM -- --overwrite-data-of-peer primary r{0..1}
else
	$DRBDADM invalidate r{0..1}
fi

service DRBD stop

