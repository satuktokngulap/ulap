#!/bin/bash
# ###########################################################
# DRBD 0.8.2.1 -> linux-cluster super-simple fencing wrapper
#
# Kills the other node in a 2-node cluster.  Only works with
# 2-node clusters (FIXME?)
#
# ###########################################################
#
# Author: Lon Hohberger <lhh[a]redhat.com> 
#
# Special thanks to fabioc on freenode
#
# http://sources.redhat.com/cluster/wiki/DRBD_Cookbook
# http://people.redhat.com/lhh/obliterate
#
# Nethesis - http://www.nethesis.it
# Federico Simoncelli <federico.simoncelli@nethesis.it>
# $Id: obliterate-peer.sh 709 2009-06-10 10:59:21Z federico $

PATH="/bin:/sbin:/usr/bin:/usr/sbin"

LOCAL_ID=$(cman_tool status | awk '/Node ID:/{print $3}')

if [ -z "$LOCAL_ID" ]; then 
	logger -t $0 "Could not determine local node ID!"
	exit 1
fi

DISK_UPTODATE=$(drbdadm get-gi $DRBD_RESOURCE | awk -F: '{print $6}')

if [ "$DISK_UPTODATE" != 1 ]; then
	logger -t $0 "Local node is not UpToDate!"
	exit 6
fi

NODECOUNT=0
while read NODE_ID NODE_NAME; do
	[ $NODE_ID = 0 ] && continue
	[ $NODE_ID != $LOCAL_ID ] && REMOTE=$NODE_NAME
	((NODECOUNT++))
done < <(cman_tool nodes | awk '!/^Node/{print $1,$NF}')

if [ $NODECOUNT -ne 2 ]; then
	logger -t $0 "Only works with 2 node clusters"
	exit 1
fi

if [ -z "$REMOTE" ]; then
	logger -t $0 "Could not determine remote node"
	exit 1
fi

logger -t $0 "Local node ID: $LOCAL_ID / Remote node: $REMOTE"

# Killing the remote node if it's still part of the cluster
cman_tool kill -n $REMOTE 2>&1 | logger -t $0

# Shoot the other guy.
for FENCE_ATTEMPT in $(seq 0 9); do 
	#
	# This could be cleaner by calling cman_tool kill -n <node>, but
	# then we have to poll/wait for fence status, and I don't feel
	# like writing that right now.  Note that GFS *will* wait for
	# this to occur, so if you're using GFS on DRBD, you still don't
	# get access. ;)
	#
	fence_node $REMOTE

	if [ $? -eq 0 ]; then
		#
		# Reference:
		# http://osdir.com/ml/linux.kernel.drbd.devel/2006-11/msg00005.html
		#
		# 7 = node got blown away.  
		#
		exit 7
	fi

        sleep 3
done

#
# Fencing failed?!
#
exit 1
