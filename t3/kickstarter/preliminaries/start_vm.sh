#!/bin/bash

LOG="logger -s $0:"

TIMEOUT=3600
LOCALNODE="`uname -n | gawk -F'.' '{print $1}'`"

$LOG "Sleep for 1 minute to wait for services to stabilize"
sleep 60

TIMER=0
$LOG "Checking if cman/rgmanager/drbd is already up..."
while [ $TIMER -ne $TIMEOUT ]; do
	#check if cman is started
	service cman status
	if [ $? -eq 0 ]; then
		#check if rgmanager is started
		service rgmanager status
		if [ $? -eq 0 ]; then
			# check if drbd is started
			service drbd status
			if [ $? -eq 0 ]; then
				$LOG "cman/rgmanager/drbd are up!"
				break
			else
				# if not started, sleep 3 seconds
				sleep 3
				TIMER=$(( $TIMER + 3 ))
			fi
		else
			# if not started, sleep 3 seconds
			sleep 3
			TIMER=$(( $TIMER + 3 ))
		fi
	else
		sleep 3
		TIMER=$(( $TIMER + 3 ))
	fi
done

if [ $TIMER -eq $TIMEOUT ]; then
	$LOG "Timed out!"
	exit 1
fi

TIMER=0
$LOG "Checking status of storage service..."
res=0
while [ $TIMER -ne $TIMEOUT ]; do
	case $(clustat -s storage_$LOCALNODE | gawk '!/Service/ && !/-------/ {print $3}') in
		started )
			$LOG "Storage service on $LOCALNODE is started"
			$LOG "Start the nfs service"
			clusvcadm -e nfs-shared
			$LOG "Checking status of VM services on $LOCALNODE"
			for VM in $(clustat | gawk '!/Service/ && !/-/ && /vm:'${LOCALNODE:1:1}'_/ {print $1}'); do
                                #if [ "$VM" == "vm:a_vm_rdpa"  -o  "$VM" == "vm:b_vm_rdpb" ]; then
				#	$LOG "$VM is marked for exclusion. Will not enable this service."
				#	continue
				#fi
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
		*)
			sleep 3
			TIMER=$(( $TIMER + 3 ))
			;;
	esac
done


if [ $TIMER -eq $TIMEOUT ]; then
	$LOG "Timed out!"
	exit 1
fi

if [ "$(clustat -s storage_$LOCALNODE | gawk '!/Service/ && !/-/ {print $3}')" != "started" ]; then
	$LOG "storage_$LOCALNODE is not started!"
	exit 2
fi

exit 0
