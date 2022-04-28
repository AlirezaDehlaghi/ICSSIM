#!/bin/bash

cd src
service openvswitch-switch start
mn -c
python init.py
screen -dmSL main python run.py
tail -f /dev/null