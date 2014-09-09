#!/bin/bash
#Restarts the X server
#Only works if X server is started from/by root

#kill /usr/bin/X process
kill $(ps aux | grep /usr/bin/X | grep -v grep | awk '{print $2}')

#restart X
/root/startup.sh
