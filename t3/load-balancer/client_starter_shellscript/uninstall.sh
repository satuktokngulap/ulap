#!/bin/bash

function die() {
    echo >&2 "$@"
    exit 1
}

#Run this script as root!
[ "$(id -u)" -eq "0" ] || die "Run with 'sudo'!"

INSTALL_FOLDER="/opt/rdpstarter"

rm -rf $INSTALL_FOLDER/
echo "Removed $INSTALL_FOLDER..."

#rm ~/Desktop/start_RDP.sh
#echo "Removed Desktop shortcuts..."

sed -i '/rdpa.tc.net/d' /etc/hosts
sed -i '/rdpb.tc.net/d' /etc/hosts

echo "Removed added hosts file entries..."

#Restore old .xinitrc file
XINITRC_FILE=~/.xinitrc

rm -rf $XINITRC_FILE

touch $XINITRC_FILE

echo "exec icewm" >> $XINITRC_FILE

echo "Restored old ~/.xinitrc..."

echo "Done!"
