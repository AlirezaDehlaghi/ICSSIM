#!/bin/bash
#cd src
#log-dir = $1
#log-file = $2
sudo chmod 777 $1

x=1; while [ $x -lt "50" ]; do ping -t 1 -c 1 192.168.0.$x | grep "byte from" |  awk '{print $4 " up"}'; let x++; done > $2

sudo chmod 777 $2
