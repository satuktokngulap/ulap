#!/bin.bash

tar czfv /var/log/$(date | awk '{printf "powerlog_%s-%s-%s.tar.gz",$6 ,$2, $3}') /var/log/power.log
echo "" > /var/log/power.log
