#!/bin/bash

#cd src
sudo chmod 777 $1
sudo python3 AttackerScapy.py --output $2 --attack scan --timeout 10  --destination '192.168.0.1/24'
sudo chmod 777 $2

