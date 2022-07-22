#!/bin/bash

#cd src
sudo chmod 777 $1
#sudo python3 ics_sim/ScapyAttacker.py --output $2 --attack replay --mode 'network' --timeout 15  --parameter 1 --destination '192.168.0.1/24'
sudo python3 ics_sim/ScapyAttacker.py --output $2 --attack replay --mode 'link' --timeout 15  --parameter 1 --destination '192.168.0.11,192.168.0.22'
sudo chmod 777 $2
