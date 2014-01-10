#!/bin/bash

LOG="logger -s $0:"

TIMEOUT=3600
LOCALNODE="`uname -n | gawk -F'.' '{print $1}'`"

$LOG "Sleep for 1 minute to wait for storage service to stabilize"
sleep 60

TIMER=0
$LOG "Checking status of storage service..."
res=0
while [ $TIMER -ne $TIMEOUT ]; do
	case $(clustat -s storage_$LOCALNODE | gawk '!/Service/ && !/-/ {print $3}') in
		started )
			$LOG "Storage service on $LOCALNODE is started"
			$LOG "Checking status of VM services on $LOCALNODE"
			for VM in $(clustat | gawk '!/Service/ && !/-/ && /vm:'${LOCALNODE:1:1}'_/ {print $1}'); do

				# Check status of VMs
				case $(clustat -s $VM | gawk '!/Service/ && !/-/ {print $3}') in
				started )
					owner=$(clustat -s $VM | gawk '!/Service/ && !/-/ {print $2}')
					$LOG "Service $VM is running on owner: $owner"
					if [ "$owner" != "`uname -n`" ]; then
						$LOG "Will migrate $VM to `uname -n`"
						clusvcadm -M $VM -m `uname -n`
					else $LOG "$VM is already started on $owner"
					fi
					;;
				"" )
					$LOG "No cluster service found for $VM"
					;;
				disabled )
					$LOG "Service $VM is disabled, will enable"
					clusvcadm -e $VM -m `uname -n`;
					;;
				* )
					$LOG "Service $VM is not started, will enable"
					clusvcadm -d $VM;
					clusvcadm -e $VM -m `uname -n`;
					;;
				esac
			done
			break
			;;
		"" )
			$LOG "No storage service for node ${LOCALNODE}"
			break
			;;
		*)
			sleep 3
			TIMER=$(( $TIMER + 3 ))
			;;
	esac
done

if [ "$(clustat -s storage_$LOCALNODE | gawk '!/Service/ && !/-/ {print $3}')" != "started" ]; then
	$LOG "Timed out waiting for storage_$LOCALNODE to start!"
	res=1
fi

exit $res
