#!/bin/bash

###################################################
# 
# Shellscript to setup Munin Monitoring
# 
# Author: Ken Salanio <kssalanio@gmail.com>
#
# Prereqs: 
#    1. /etc/hosts already setup with 
#       hostnames for local vms and baremetal
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
#    3. SNMP is installed on all VMs and 
#       baremetal nodes, with configured 
#       'CLOUDTOPT3' as read-only community
#
###################################################

LOG_TO_MESSAGES=""
SNMP_V3_PWD="muninpasswd"
HOSTNAME=$(hostname)
MGMT_IP_ADDR=$(ifconfig br0 | grep 'inet addr' | cut -d':' -f2 | cut -d' ' -f1)
[[ -z $MGMT_IP_ADDR ]] && $(ifconfig eth0 | grep 'inet addr' | cut -d':' -f2 | cut -d' ' -f1) || die "Cannot find IP address in interfaces 'br0' or 'eth0'"

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

function create_munin_snmp_plugins(){
  echo -ne "Creating SNMP plugins for $1... "
  declare -a SYMLINKS=$(munin-node-configure --shell --snmp $1 --snmpversion 2c --snmpcommunity CLOUDTOPT3)

  while read -r LINE; do
	eval $LINE
  done <<< "$SYMLINKS"
  echo "Done!"
}

[[ $EUID -ne 0 ]] && die "Munin setup script must be run as root" 1>&2

#Create temporary folder
#log_info "Creating tmp dir"
#mkdir tmp
#cd ./tmp
#Install epel repo
yum install -y wget
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
yum install -y net-snmp net-snmp-utils net-snmp-libs
cp /etc/snmp/snmpd.conf /etc/snmp/snmpd.conf.bak
#configure snmp V3 adn V2
net-snmp-create-v3-user -ro -A ${SNMP_V3_PWD} -X ${SNMP_V3_PWD} snmpuser
echo "rocommunity CLOUDTOPT3" > /etc/snmp/snmpd.conf
echo "rouser snmpuser authpriv" >> /etc/snmp/snmpd.conf
#Replace SNMP logging opts to prevent flooding logs
sed -i "s/-LS0-6d -Lf/-LS0-4d -Lf/g" /etc/init.d/snmpd
chkconfig --levels 235 snmpd on
service snmpd start

#>>Install and setup Munin
log_info "Installing Munin..."
yum install -y telnet nginx httpd-tools munin munin-node
[[ -d "/usr/share/nginx/logs" ]] || mkdir /usr/share/nginx/logs
#create htpasswd file
touch /var/www/html/munin/.htpasswd
 
# NOTE:Skipping this part
# Create munin website user and password via expect
#~ log_info "Configure password for muninuser..."
#~ yum install -y expect
#~ expect -c "
#~ spawn htpasswd -c /var/www/html/munin/.htpasswd muninuser
#~ expect {
    #~ -re { password: $} {
        #~ send \"$SNMP_V3_PWD\r\"
        #~ exp_continue
    #~ }
#~ }
#~ "

#>>Nginx config
log_info "Configuring nginx..."
chown -R munin:munin /var/www/html/munin
cp "$(get_script_dir)/utils/munin-site.conf" /etc/nginx/conf.d/munin-site.conf
sed -i "s/<NETWORK_IP>/$(echo $MGMT_IP_ADDR | cut -d'.' -f1-3)\.0/g" /etc/nginx/conf.d/munin-site.conf
chkconfig nginx --levels 235 on

#>>Munin config
log_info "Configuring munin..."
#configure snmp communities for munin
touch /etc/munin/plugin-conf.d/snmp_communities
cat >/etc/munin/plugin-conf.d/snmp_communities <<EOL
[snmp_*]
env.community CLOUDTOPT3
EOL
chkconfig --levels 235 munin-node on

#Node specific config
#select appropriate munin config template

SCRIPT_DIR=$(get_script_dir)
#Node A
if [[ $(hostname | grep "sa") ]]; then
cp "$SCRIPT_DIR/utils/sa.munin.conf" /etc/munin/munin.conf
create_munin_snmp_plugins "sa.local"
create_munin_snmp_plugins "ldap.local"
create_munin_snmp_plugins "rdpa.local"
#Node B
elif [[ $(hostname | grep "sb") ]]; then
cp "$SCRIPT_DIR/utils/sb.munin.conf" /etc/munin/munin.conf
create_munin_snmp_plugins "sb.local"
create_munin_snmp_plugins "lms.local"
create_munin_snmp_plugins "rdpb.local"
else
die "Hostname does not identify if node is 'sa' or 'sb'!"
fi

#Selinux policies
#yum install -y policycoreutils-python

#Start/restart services
[ $(ps aux | grep -c 'munin-node') -gt 1 ] && service munin-node restart || service munin-node start
[ $(ps aux | grep -c 'nginx') -gt 1 ] && service nginx restart || service nginx start
