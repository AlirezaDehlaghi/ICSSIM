#!/bin/bash

#cd src
sudo chmod 777 ./attacks/attack-logs/

x=1; while [ $x -lt "50" ]; do ping -t 1 -c 1 192.168.0.$x | grep "byte from" |  awk '{print $4 " up"}'; let x++; done > ./attacks/attack-logs/scan_ping.txt

sudo chmod 777 ./attacks/attack-logs/ip_ping.txt
