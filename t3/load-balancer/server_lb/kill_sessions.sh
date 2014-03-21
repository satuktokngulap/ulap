#!/bin/sh

EXCLUDE_PATTERN="root\|rdpadmin"

kill_usr_list=$(ps aux | grep 'xrdp-sessvc' | grep -v $EXCLUDE_PATTERN)
IFS=$'\n'
for LINE in ${kill_usr_list} ; do
    usr=$(echo $LINE | cut -d' ' -f1)
    echo "Killing processes owned by [$usr]"
    pkill -9 -u $usr
done
