#!/bin/bash

###################################################
# 
# Shellscript called by cron to create scheduled backups
# 
# Author: Ken Salanio <kssalanio@gmail.com>
#
###################################################

ARCHIVE_DIR="/var/archive/"
#TARGET_DIR="/shared/files/home/Paganini/"
TARGET_DIR="/shared/files/home/"
FILE_PREFIX="accounts_backup_"
FAILED_LOG_FILE="/shared/archive/failed.log"

function die() {
    #echo >&2 "[BACKUP_SCRIPT] $@"
    logger >&2 "[BACKUP-CRON] $@"
    exit 1
}

function log_info(){
    #echo "[BACKUP_SCRIPT] $@"
    logger "[BACKUP-CRON] $@"
}

function log_error(){
    #echo "[BACKUP_SCRIPT] $@"
    logger "[BACKUP-CRON][ERROR!] $@"
}

#Check if a backup script is running now
[ $(ps aux | grep -c 'backup_restore.sh') -gt 2 ] && die "A restore backup script is currently running! Please wait before trying again."
[ $(ps aux | grep -c 'backup_manual.sh') -gt 2 ] && die "A manual backup script is currently running! Please wait before trying again."
[ $(ps aux | grep -c 'backup_cron.sh') -gt 3 ] && die "A scheduled backup script is currently running! Please wait before trying again."

#Check directories
[ -d $TARGET_DIR ] || die "Cannot find target directory [$TARGET_DIR]"
[ -d $ARCHIVE_DIR ] || die "Cannot find archive directory [$ARCHIVE_DIR]"

#Check log file for failed backups. Create if non exists
[ -f $FAILED_LOG_FILE ] || touch $FAILED_LOG_FILE

#Get current date
DATE=$(date +%Y%m%d)
HOUR=$(date +%H)

#Log to failed.log, delete later if successful
CURRENT_TIME=$(date +%Y/%m/%d-%H:%M:%S)
echo "Incomplete scheduled backup on $CURRENT_TIME" >> $FAILED_LOG_FILE

#Create Backup
NEW_BACKUP="$ARCHIVE_DIR$FILE_PREFIX$DATE-$HOUR.tar.gz"

#Check if file was already created
if [ -f $NEW_BACKUP ]
then
    log_info "Failed creating $NEW_BACKUP, file already exists!"
else
    #Check if more than 7 files
    NUM_FILES=$(ls -lah $ARCHIVE_DIR | grep -c "$FILE_PREFIX")
    if [ $NUM_FILES -ge 7 ]
    then                                                                        # if more than 7 scheduled backup files
        OLDEST_BACKUP=$(ls -a $ARCHIVE_DIR | sort | grep -m 1 "$FILE_PREFIX")   # find the oldest backup file
        rm -rf "$ARCHIVE_DIR$OLDEST_BACKUP"                                     # delete oldest backup file
        log_info "Counted 7 backup files. Deleted oldest: $OLDEST_BACKUP"
    fi

    #Create the backup file
    logger "[BACKUP_SCRIPT] Creating new backup file for accounts in $NEW_BACKUP"
    RESULT=$(tar -czvf ${NEW_BACKUP} $TARGET_DIR)
    if [ -z $(echo $RESULT | grep "Exiting with failure") ]                     # see if tar failed
    then
        log_info "Successfully created new file $NEW_BACKUP"
    else                                                                        # if tar failed, log failure
        
        #Trim first line if failed.log if it exceeds 20 lines
        [[ $(wc -l < failed.log) -gt 20 ]] && sed -i -e "1d" $FAILED_LOG_FILE 
        
        #exit with error
        die "[ERROR!]: $RESULT"      
    fi 
fi

#Delete previously added entry from failed.log
#sed -i '/Incomplete scheduled backup on $CURRENT_TIME/d' $FAILED_LOG_FILE 
sed -i '$ d' $FAILED_LOG_FILE 
