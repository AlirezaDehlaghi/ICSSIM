#!/bin/bash

#cd src
sudo chmod 777 $1
#sudo python3 ics_sim/ScapyAttacker.py --output $2 --attack replay --timeout 15  --parameter 3 --target '192.168.0.1/24'
sudo python3 ics_sim/ScapyAttacker.py --output $2 --attack replay --timeout 15  --parameter 3 --target '192.168.0.11,192.168.0.22'
sudo chmod 777 $2
