#!/bin/bash
#Command line args:
#  $1 is vm_rdpa IP address
#  $2 is vm_rdpb IP address

function die() {
    echo >&2 "$@"
    exit 1
}

#run script as root!
[ "$(id -u)" -eq "0" ] || die "Run as root!"

[ "$#" -eq 2 ] || die "Requires 2 arguments (RDP VM IP adresses), $# arguments provided"

IP_PATTERN='^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$'
echo $1 | grep -E -q $IP_PATTERN || die "Invalid IP address for 1st argument, <$1> provided"
echo $2 | grep -E -q $IP_PATTERN || die "Invalid IP address for 2nd argument, <$2> provided"

#check script folder
pushd `dirname $0` > /dev/null
SCRIPT_FOLDER=`pwd`
popd > /dev/null

echo "Running script from '$SCRIPT_FOLDER'"

echo "Checking xfreerdp symlink..."
#XFREERDP_SYMLINK="/usr/local/bin/xfreerdp"
XFREERDP_SYMLINK="/usr/bin/xfreerdp"
[ -f "$XFREERDP_SYMLINK" ] || ln -s /opt/freerdp/bin/xfreerdp $XFREERDP_SYMLINK  #Create xfreerdp symlink if it does not exist

#check/make install folder
INSTALL_FOLDER="/opt/rdpstarter"

[ -d "$INSTALL_FOLDER" ] || mkdir $INSTALL_FOLDER   #Create folder if it doesn't exist

echo "Installing in: '$INSTALL_FOLDER'"

echo "Copying to install folder..."
#copy executable, config, and icon to target folder
chmod +x $SCRIPT_FOLDER/src/*
cp $SCRIPT_FOLDER/src/* $INSTALL_FOLDER/
#chmod +x $INSTALL_FOLDER/client_starter.sh

#echo "Copying Desktop shortcuts..."

##  OR copy executing shellscript to Desktop
#cp $SCRIPT_FOLDER/src/start_RDP.sh ~/Desktop/
#chmod +x ~/Desktop/start_RDP.sh
#chown $SUDO_USER:$SUDO_USER ~/Desktop/start_RDP.sh

echo "Appending to /etc/hosts..."
#append rdpa.tc.net and rdpb.tc.net to hosts file
#  with their corresponding IPs
echo "$1    rdpa.tc.net" >> /etc/hosts
echo "$2    rdpb.tc.net" >> /etc/hosts

#XINITRC_FILE=/root/.xinitrc
XINITRC_FILE=~/.xinitrc
#XINITRC_FILE=/etc/X11/xinit/xinitrc

echo "Adding RDP to $XINITRC_FILE"
if [ -z $(cat $XINITRC_FILE | grep "~/opt/rdpstarter/client_starter.sh") ] #if script has not been added before
then 
    #backup old .xinitrc
    cp $XINITRC_FILE $XINITRC_FILE.bak
    
    #comment all lines in $XINITRC
    awk '{print "#" $0;}' $XINITRC_FILE > awk_out.tmp && mv awk_out.tmp $XINITRC_FILE
    
    #add xterm and script to x startup
    echo "xterm &" >> $XINITRC_FILE
    echo "exec /opt/rdpstarter/client_starter.sh" >> $XINITRC_FILE
fi
echo "Done!"
