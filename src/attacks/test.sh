#!/bin/bash

timeout = 30
noise = 0.1
destination = '192.168.0.1/24'

if [ "$#" -gt 0 ]; then
    timeout = "$1"
fi

if [ "$#" -gt 1 ]; then
    noise = "$2"
fi

if [ "$#" -gt 2 ]; then
    destination = "$3"
fi

if [ "$#" -gt 3 ]; then
    echo "Usage: $0 arg1 arg2 arg3"
    exit 1
fi

sudo python3 ics_sim/ScapyAttacker1.py --output $2 --attack mitm --timeout 30  --parameter 0.1 --destination '192.168.0.1/24'