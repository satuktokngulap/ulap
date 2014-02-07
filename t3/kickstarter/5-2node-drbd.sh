#!/bin/bash

DRBDADM="/sbin/drbdadm"

$DRBDADM dump
if [ $? -ne 0 ]; then
	echo "Please review configuration files!"
	exit 1;
fi

$DRBDADM create-md r{0..1}

# Force node sa to be primary
MYNAME="`uname -n`"
if [ "$(echo $MYNAME | gawk -F'.' '{print $1}')" = "sa" ]; then
	modprobe drbd
	$DRBDADM attach r{0..1}
	$DRBDADM -- --clear-bitmap new-current-uuid r{0..1}
	$DRBDADM new-current-uuid r{0..1}
else
	service drbd start #If node b, simply start drbd and connect to sa
	$DRBDADM up r{0..1}
fi
