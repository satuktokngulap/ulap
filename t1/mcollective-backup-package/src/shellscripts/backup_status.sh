#!/bin/bash

###################################################
# 
# Shellscript for checking the status of backup files
# 
# Author: Ken Salanio <kssalanio@gmail.com>
#
###################################################

ARCHIVE_DIR="/var/archive/"
FILE_PREF1="accounts_backup_"
FILE_PREF2="manual_backup_"
FILE_PREF3="restore_backup_"

function die() {
    #echo >&2 "[BACKUP_SCRIPT] $@"
    logger >&2 "[BACKUP-STATUS] $@"
    exit 1
}

#Check directories
[ -d $ARCHIVE_DIR ] || die "Cannot find archive directory [$ARCHIVE_DIR]"

CRON_FILES=$(ls -lah $ARCHIVE_DIR | sort | grep -c $FILE_PREF1)
MANUAL_FILES=$(ls -lah $ARCHIVE_DIR | sort | grep -c $FILE_PREF2)
RESTORE_FILES=$(ls -lah $ARCHIVE_DIR | sort | grep -c $FILE_PREF3)

#Get date yesterday
NOW=$(date +%Y%m%d)
YTD=$(date --date="1 days ago" +%Y%m%d)

#Check existence of yesterday or today's scheduled/manual backup file
SCHEDULED_STATUS="Outdated"
if [ -f "$ARCHIVE_DIR$FILE_PREF1$YTD.tar.gz" ] || [ -f "$ARCHIVE_DIR$FILE_PREF2$YTD.tar.gz" ] || [ -f "$ARCHIVE_DIR$FILE_PREF3$YTD.tar.gz" ] || [ -f "$ARCHIVE_DIR$FILE_PREF1$NOW.tar.gz" ] || [ -f "$ARCHIVE_DIR$FILE_PREF2$NOW.tar.gz" ] || [ -f "$ARCHIVE_DIR$FILE_PREF3$NOW.tar.gz" ]
then
    SCHEDULED_STATUS="UpToDate"
fi

if [ $# -eq 1 ] && ( [ "$1" == "--files" ] || [ "$1" == "-F" ] )
then
    echo $(ls $ARCHIVE_DIR* | grep tar.gz)
else
    echo "$CRON_FILES/$MANUAL_FILES/$SCHEDULED_STATUS"
fi

