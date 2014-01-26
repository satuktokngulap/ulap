#!/bin/bash

MYNAME="`uname -n`"
MYCLUSTER="$(echo $MYNAME | gawk -F'.' '{print $2}')"

if [ "$(echo $MYNAME | gawk -F'.' '{print $1}')" = "sa" ]; then
        mkfs.gfs2 -p lock_dlm -j 2 -t ${MYCLUSTER:0:6}cluster:shared /dev/shared-vg0/shared
fi

mkdir /shared
mount /dev/shared-vg0/shared /shared/
df -hP /shared

echo `gfs2_tool sb /dev/shared-vg0/shared uuid | awk '/uuid =/ { print $4; }' | sed -e "s/\(.*\)/UUID=\L\1\E \/shared\t\tgfs2\tdefaults,noatime,nodiratime\t0 0/"` >> /etc/fstab

service gfs2 status

if [ "$(echo $MYNAME | gawk -F'.' '{print $1}')" = "sa" ]; then
mkdir -p /shared/system/definitions
mkdir -p /shared/files/{moodle,home}
fi

chkconfig cman on && chkconfig rgmanager on

