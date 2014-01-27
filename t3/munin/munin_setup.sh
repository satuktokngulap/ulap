#!/bin/bash

###################################################
# 
# Shellscript to setup Munin Monitoring
# 
# Author: Ken Salanio <kssalanio@gmail.com>
#
# Prereqs: 
#    1. /etc/hosts already setup with 
#       hostnames for local vms
#
#    2. open the following ports 
#
#        *tcp ports, restricted to local subnet:
#          - 8000 (http server)
#          - 23 (telnet)
#          - 4949 (munin)
#
#        *upd ports, restricted to local subnet:
#          - 161:162 (snmp)
#
###################################################

LOG_TO_MESSAGES=""
SNMP_V3_PWD="cedricthegreat"
HOSTNAME=$(hostname)
MGMT_IP_ADDR=$(ifconfig eth0 | grep 'inet addr' | cut -d':' -f2 | cut -d' ' -f1)

function log_info(){
    [[ $LOG_TO_MESSAGES ]] && logger >&2 "[MUNIN_SETUP] $@" || echo >&2 "[MUNIN_SETUP] $@"
}

function die() {
    [[ $LOG_TO_MESSAGES ]] && logger >&2 "[MUNIN_SETUP][EXIT] $@" || echo >&2 "[MUNIN_SETUP][EXIT] $@"
    exit 1
}

function log_error(){
    [[ $LOG_TO_MESSAGES ]] && logger >&2 "[MUNIN_SETUP][ERROR] $@" || echo >&2 "[MUNIN_SETUP][ERROR] $@"
}

function get_script_dir(){
  SOURCE="${BASH_SOURCE[0]}"
  while [ -h "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
    DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
    SOURCE="$(readlink "$SOURCE")"
    [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE" # if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
  done
  echo "$( cd -P "$( dirname "$SOURCE" )" && pwd )"
}

[[ $EUID -ne 0 ]] && die "Munin setup script must be run as root" 1>&2

die $(get_script_dir)

#Create temporary folder
log_info "Creating tmp dir"
mkdir tmp
cd ./tmp

#Setup epel repo
log_info "Setting epel repo..."
if [[ $(ls /etc/yum.repos.d/ | grep epel) ]]
then
  log_info "epel repo already installed"
else
  wget http://ftp.riken.jp/Linux/fedora/epel/6/i386/epel-release-6-8.noarch.rpm
  rpm -ivh epel-release-6-8.noarch.rpm
fi

#>>Install and setup SNMP
log_info "Installing SNMP..."
yum install net-snmp net-snmp-utils net-snmp-libs
cp /etc/snmp/snmpd.conf /etc/snmp/snmpd.conf.bak
#configure snmp V3 adn V2
net-snmp-create-v3-user -ro -A ${SNMP_V3_PWD} -X ${SNMP_V3_PWD} snmpuser
echo “rocommunity CLOUDTOPT3” > /etc/snmp/snmpd.conf
echo “rouser snmpuser authpriv” >> /etc/snmp/snmpd.conf
#Replace SNMP logging opts to prevent flooding logs
sed -i "s/-LS0-6d -Lf/-LS0-4d -Lf/g" /etc/init.d/snmpd

#>>Install and setup Munin
log_info "Installing Munin..."
yum install telnet nginx httpd-tools munin munin-node
mkdir /usr/share/nginx/logs
#create htpasswd file and create <muninuser>
touch /var/www/html/munin/.htpasswd
log_info "Enter password for muninuser:"
htpasswd -c /var/www/html/munin/.htpasswd muninuser   #TODO:Need expect to automatically enter password

#>>Nginx config
log_info "Configuring nginx..."
chown -R munin:munin /var/www/html/munin
cp "$(get_script_dir)/utils/munin-site.conf" /etc/nginx/conf.d/munin-site.conf
sed -i "s/<NETWORK_IP>/$(echo $MGMT_IP_ADDR | cut -d'.' -f1-3)\./g" /etc/nginx/conf.d/munin-site.conf
chkconfig nginx --levels 235 on

#>>Munin config
log_info "Configuring munin..."
#select appropriate munin config template
MUNIN_CONFIG=$(get_script_dir)
[[ $(echo $MGMT_IP_ADDR | cut -d'.' -f4) -eq 11 ]] && MUNIN_CONFIG="$MUNIN_CONFIG/utils/sa.munin.conf" || MUNIN_CONFIG="$MUNIN_CONFIG/utils/sb.munin.conf"
cp $MUNIN_CONFIG /etc/munin/munin.conf
chkconfig --levels 235 munin-node on
#configure snmp communities for munin
touch /etc/munin/plugin-conf.d/snmp_communities
cat >/etc/munin/plugin-conf.d/snmp_communities <<EOL
[snmp_*]
env.community CLOUDTOPT3
EOL

#Restart services
service munin-node restart
service nginx restart
