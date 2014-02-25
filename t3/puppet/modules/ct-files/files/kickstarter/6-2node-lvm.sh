#!/bin/bash

service cman start
/etc/init.d/clvmd start
chkconfig clvmd off

chkconfig modclusterd on
chkconfig ricci on
service modclusterd start

clvmd -R

MYNAME="`uname -n`"
MYCLUSTER="$(echo $MYNAME | gawk -F'.' '{print $1}')cluster"

if [ "$(echo $MYNAME | gawk -F'.' '{print $1}')" = "sa" ]; then
	pvcreate /dev/drbd{0..1}
	pvscan

	vgcreate -c y shared-vg0 /dev/drbd1
	vgcreate -c y sa-vg0 /dev/drbd0
	vgcreate -c y sb-vg0 /dev/drbd0
	vgscan
	
	lvcreate -l 100%FREE -n shared shared-vg0
	lvcreate -L 12G -n a_vm_rdpa sa-vg0
	lvcreate -L 8G -n a_vm_ldap sa-vg0
	lvcreate -L 12G -n b_vm_rdpb sa-vg0
	lvcreate -L 8G -n b_vm_lms sa-vg0
	lvcreate -L 12G -n a_vm_rdp_mint sa-vg0
	lvscan

fi

echo ""
echo "LVM Partitions:"
pvscan; vgscan; lvscan

