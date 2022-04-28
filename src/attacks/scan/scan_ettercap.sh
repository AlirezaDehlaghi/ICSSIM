#!/bin/bash

#cd src
sudo chmod 777 ./attacks/attack-logs/

sudo -S ettercap -Tq -Q   --save-hosts ./attacks/attack-logs/ip_ettercap.txt -i eth0  

sudo chmod 777 ./attacks/attack-logs/ip_ettercap.txt

