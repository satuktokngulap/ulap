#/bin/bash
SWITCH='10.18.221.210'
CMD='date'
CLUS='/usr/sbin/clusvcadm'

#regex here
HOUR=`date | grep -P '\ [0-2][0-9]\:' -o | sed 's/\://g'`
MINUTE=`date | grep -P '\\:[0-2][0-9]\:' -o | sed 's/\://g'`
DATE=`date | awk '{ if ($3 ~ /^[0-9]$/) {print 0$3} else {print $3} }'`

/usr/bin/ipmitool -H ${SWITCH} -U Admin -P Admin raw 0x30 0x33
sleep 2
/usr/bin/ipmitool -H ${SWITCH} -U Admin -P Admin raw 0x30 0x38 06 ${DATE} 20 14 ${HOUR} 45

$CLUS -d service:nfs-shared
$CLUS -d vm:a_vm_ldap
$CLUS -d vm:a_vm_rdpa
$CLUS -d vm:b_vm_rdpb
$CLUS -d vm:b_vm_lms

logger "shutting down via cronjob marker"
ssh root@10.18.221.12 "poweroff"
poweroff
