#!/bin/bash

#cd src
sudo echo 0 > /proc/sys/net/ipv4/ip_forward
sudo python3 AttackerScapy.py --output $2 --attack mitm --timeout 15  --parameter 5 --destination '192.168.0.1/24'
#sudo python3 Replay.py
sudo echo 1 > /proc/sys/net/ipv4/ip_forward
