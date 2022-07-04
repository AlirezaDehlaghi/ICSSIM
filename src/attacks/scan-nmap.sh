#!/bin/bash

#cd src
#log-dir = $1
#log-file = $2
sudo chmod 777 $1


nmap -p- -oN $2 192.168.0.1-255

sudo chmod 777 $2


