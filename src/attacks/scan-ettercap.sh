#!/bin/bash
#cd src
#log-dir = $1
#log-file = $2
sudo chmod 777 $1

sudo -S ettercap -Tq -Q   --save-hosts $2 -i eth0
#sudo -S ettercap -Tq -Q   --save-hosts ./../ics_sim/attacks/attack-logs/scan_ettercap.txt -i eth0

sudo chmod 777 $2

