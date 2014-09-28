#!/bin/bash

counter=0
store_pid=1
users_id=1
i=0

log_file="/var/log/xrdp.log"
process="Xorg"
process2="Xorg"

# store user name and pids of running process in separate arrays
#for s in `ps -C $process -o pid=,user=,command=`
for s in `ps -C $process -o pid=,user=`
do
    #additional check to stop the loop?
    echo "string $s"
    if [ $store_pid -eq 1 ]; then
        pids[$counter]=$s
	#echo "storing PID" 
       	store_pid=0
    elif [ $users_id -eq 1 ]; then
        users[$counter]=$s
	#echo "storing user"
        users_id=0
    fi
    if [ $store_pid -eq 0 ] && [ $users_id -eq 0 ]; then
        users_id=1
        ((counter++))
    fi
done
 
pids2=`ps -C $process -o pid=`
ip_counter=0
for p in $pids2
do
    #base IP address determined but not printed
    ip=`grep X11rdp_pid=$p $log_file | awk '{printf(" IP=%s",substr($11,11,23))}'`
    ip_addresses[$ip_counter]=$ip
    ((ip_counter++))
    #echo $ip
    #grep X11rdp_pid=$p $log_fie | awk -F= '{print $6}' | awk '{print $1}'
done


# this is just for testing - delete when done
echo -e "counter=$counter\n"
for ((i = 0; i < counter; i++))
do
    echo -e "${users[$i]} ${pids[$i]} ${ip_addresses[$i]}\n"
done
