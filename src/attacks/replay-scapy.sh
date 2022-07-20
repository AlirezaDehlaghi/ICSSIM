#!/bin/bash

#cd src
sudo chmod 777 $1
sudo python3 AttackerScapy.py --output $2 --attack replay --timeout 15  --parameter 3 --destination '192.168.0.1/24'
sudo chmod 777 $2
