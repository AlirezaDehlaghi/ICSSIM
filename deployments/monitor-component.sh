#!/bin/bash

# Check Args #

if [ $# != 1 ]; then
	echo "Need 1 Argument: ICS Component name."
	
	exit
fi


# Check Args Value

if [ $1 = "plc1" ] || [ $1 = "plc2" ] || [ $1 = "hmi1" ] || [ $1 = "hmi2" ] || [ $1 = "hmi3" ] || [ $1 = "pys" ] || [ $1 = "attacker" ] || [ $1 = "attacker-machine" ]
then 
	# Mian command
	sudo docker container attach $1
else
	echo "ICS component <$1> is not recognizable! "
	echo "Acceptable ICS Compnents:
	PLC1
	PLC2
	HMI1
	HMI2
	HMI3
	FactorySimulation
	Attacker
	AttackerMachine"
fi





