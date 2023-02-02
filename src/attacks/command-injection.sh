#!/bin/bash

#cd src
sudo chmod 777 $1

python3 CommandInjectionAgent.py 30

sudo chmod 777 $2
