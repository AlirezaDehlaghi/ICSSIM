#!/bin/bash
log-dir = $1
log-file = $2
sudo chmod 777 $1
echo "">$2
python3 DDosAgent.py 'A' &
python3 DDosAgent.py 'B' &
python3 DDosAgent.py 'C' &
python3 DDosAgent.py 'D' &
#python3 DDosAgent.py 'E' &
#python3 DDosAgent.py 'F' &
#python3 DDosAgent.py 'G' &
#python3 DDosAgent.py 'H' &
#python3 DDosAgent.py 'I' &
python3 DDosAgent.py 'J'

sudo chmod 777 $2
