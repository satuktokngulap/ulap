#!/bin/bash

###################################################
# 
# Shellscript called for remotely restoring backups
# 
# Author: Ken Salanio <kssalanio@gmail.com>
#
###################################################

ARCHIVE_DIR="/var/archive/"
MANUAL_BACKUP="/shared/scripts/backup/backup_manual.sh"
HOME_DIR="/shared/files/home/"
UNTAR_DIR="/"

function die() {
    echo >&2 "$@"
    logger >&2 "[BACKUP-RESTORE] $@"
    exit 1
}

function log_info(){
    #echo "[BACKUP_SCRIPT] $@"
    logger "[BACKUP-RESTORE] $@"
}

#Check if a backup script is running now
[ $(ps aux | grep -c 'backup_restore.sh') -gt 3 ] && die "A restore backup script is currently running! Please wait before trying again."
[ $(ps aux | grep -c 'backup_manual.sh') -gt 2 ] && die "A manual backup script is currently running! Please wait before trying again."
[ $(ps aux | grep -c 'backup_cron.sh') -gt 2 ] && die "A scheduled backup script is currently running! Please wait before trying again."

#input validation
[ $# -ne 1 ] && die "No backup file specified to restore from!"
[ -f $1 ] || die "File $1 does not exist!"
[[ (! $1 == *accounts_backup_*) && (! $1 == *manual_backup_*) && (! $1 == *restore_backup_*) ]] && die "File $1 is not a valid backup file!"

#check time, only execute on off hours
HOUR=$(date +%H)
[[ ( $HOUR -gt 6) && ( $HOUR -lt 20) ]] && die "Remote restore can only be executed during off hours! Current time is $(date +%H:%M:%S)"

#disable RDP VMs
log_info "Disabling RDP VMs..."
if [ $(command -v clusvcadm) ]
then
    clusvcadm -d vm:a_vm_rdpminta
    clusvcadm -d vm:b_vm_rdpmintb
else
    log_info "[clusvcadm] binary not found, skipping disabling RDP VMs"
fi

#create manual backup of current
log_info "Creating backup file before restoring..."

DATE=$(date +%Y%m%d)
RESTORE_BACKUP="${ARCHIVE_DIR}restore_backup_$DATE.tar.gz" 
#Evaluate if there is duplicate
IDX=1
while [ -f $RESTORE_BACKUP ]
do
    RESTORE_BACKUP="$(echo $RESTORE_BACKUP |  cut  -d '.' -f1 |  cut  -d '-' -f1)-$IDX.tar.gz"
    IDX=$(( $IDX + 1 ))
done
TAR_RESULT=$(tar -czvf ${RESTORE_BACKUP} $HOME_DIR)
log_info "Successfully created file [$RESTORE_BACKUP]"

#delete home folder contents
log_info "Deleting home folders..."
rm -rf $HOME_DIR*

#untar chosen backup file
log_info "Decompressing chosen backup file [$1]..."
tar xzvf $1 -C $UNTAR_DIR > /dev/null 2>&1

log_info "Re-enabling RDP VMs..."
if [ $(command -v clusvcadm) ]
then
    clusvcadm -e vm:a_vm_rdpminta
    clusvcadm -e vm:b_vm_rdpmintb
fi
    
log_info "Done"

echo "Restore Successful!"
echo "Created: $RESTORE_BACKUP"
