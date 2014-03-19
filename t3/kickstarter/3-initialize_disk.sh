#!/bin/bash
# CloudTop: T3 2-Node DRBD Configuration v0.01
# This script initializes the disk that would be used as DRBD device.
#
# Author: Isabel Montes
# Date: February 25, 2014

PROGNAME="CloudTop T3 Disk Initialize:"

logger "$PROGNAME Start at `date`"
echo "$PROGNAME Initializing disks..."
logger "$PROGNAME Initializing /dev/sda5..."
dd if=/dev/zero of=/dev/sda5 bs=4M > devsda5.ddlog

logger "$PROGNAME Initializing /dev/sdb1..."
dd if=/dev/zero of=/dev/sdb1 bs=4M > devsdb1.ddlog

logger "$PROGNAME Done at `date`"
