#!/bin/bash

###################################################
# 
# Shellscript for manually creating backups
# 
# Author: Ken Salanio <kssalanio@gmail.com>
#
###################################################

ARCHIVE_DIR="/var/archive/"
#TARGET_DIR="/shared/files/home/Paganini/"
TARGET_DIR="/shared/files/home/"
FILE_PREFIX="manual_backup_"

function die() {
    echo >&2 "[ERROR] $@"
    logger >&2 "[BACKUP-MANUAL] $@"
    exit 1
}

function log_info(){
    #echo "[BACKUP_SCRIPT] $@"
    logger "[BACKUP-MANUAL] $@"
}

function log_error(){
    #echo "[BACKUP_SCRIPT] $@"
    logger "[BACKUP-MANUAL][ERROR!] $@"
}

#Check if a backup script is running now
[ $(ps aux | grep -c 'backup_restore.sh') -gt 2 ] && die "A restore backup script is currently running! Please wait before trying again."
[ $(ps aux | grep -c 'backup_manual.sh') -gt 3 ] && die "A manual backup script is currently running! Please wait before trying again."
[ $(ps aux | grep -c 'backup_cron.sh') -gt 2 ] && die "A scheduled backup script is currently running! Please wait before trying again."

#Check directories
[ -d $TARGET_DIR ] || die "Cannot find target directory [$TARGET_DIR]"
[ -d $ARCHIVE_DIR ] || die "Cannot find archive directory [$ARCHIVE_DIR]"

#Get current date
DATE=$(date +%Y%m%d)

#Backup filename
NEW_BACKUP="$ARCHIVE_DIR$FILE_PREFIX$DATE.tar.gz"

#Evaluate if there is duplicate
IDX=1
while [ -f $NEW_BACKUP ]
do
#    echo "[BACKUP_SCRIPT] File already exists! Appending suffix: [$IDX]"
    NEW_BACKUP="$ARCHIVE_DIR$FILE_PREFIX$DATE-$IDX.tar.gz"
    IDX=$(( $IDX + 1 ))
done

#Create backup file
log_info "creating new backup file for accounts in $NEW_BACKUP"
RESULT=$(tar -czvf ${NEW_BACKUP} $TARGET_DIR)

if [ -z $(echo $RESULT | grep "Exiting with failure") ]
then
    log_info "Successfully created new file $NEW_BACKUP"
    echo "Created:$NEW_BACKUP"
else
    die "[ERROR!]:$RESULT"      
fi 
