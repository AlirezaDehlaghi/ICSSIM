#!/bin/bash

#cd src
sudo chmod 777 ./attacks/attack-logs/	

nmap -p- -oN ./attacks/attack-logs/ip_nmap.txt 192.168.0.1-255 

sudo chmod 777 ./attacks/attack-logs/ip_nmap.txt


