#!/bin/bash

service iptables stop

DRBDADM="/sbin/drbdadm"

$DRBDADM dump
if [ $? -ne 0 ]; then
	echo "Please review configuration files!"
	exit 1;
fi

$DRBDADM create-md r0
$DRBDADM create-md r1
modprobe drbd
$DRBDADM up r{0..1}
echo "Waiting for resources to connect..."
$DRBDADM wait-connect r{0..1}
if [ $? -ne 0 ]; then
	echo "Timed out waiting for resources to connect!!"
	exit 1;
fi

# Force node sa to be primary
MYNAME="`uname -n`"
if [ "$(echo $MYNAME | gawk -F'.' '{print $1}')" = "sa" ]; then
	$DRBDADM -- --clear-bitmap new-current-uuid r{0..1}
fi

# sleep after clearing bitmap
sleep 5

echo "Restarting drbd..."
service drbd restart
