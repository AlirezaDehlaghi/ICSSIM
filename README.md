
# ICSSIM
This is the ICSSIM source code and user manual for simulating industrial control system testbed for cybersecurity experiments


## Run a Sample Bottle Filling Factory

### Run in Docker container Environement

#### Pre steps
Make sure that you have already installed the following applications and tools. 

* git
* Docker
* Docker-Compose

#### Getting ICSSIM and the sample project
Clone The probject into your local directory using following git command.
```
git clone https://github.com/AlirezaDehlaghi/ICSSIM ICSSIM
```

check the file [Configs.py](src/Configs.py) and make sure that EXECUTION_MODE varibale is set to EXECUTION_MODE_DOCKER as follow:
```
EXECUTION_MODE = EXECUTION_MODE_DOCKER
```

#### Running the sample project 
Run the sample project using the prepared script 
[init.sh](deployments/init.sh)
```
cd ICSSIM/deployments
./init.sh
```
#### Check successful running
If *init.sh* commands runs to the end, it will show the status of all containers. In the case that all containers are 'Up', then project is running successfully.
You could also see the status of containers with following command:
```
sudo docker-compose ps
```

#### Operating the control system and apply cyberattacks
In the directory [deployments](deployments/) there exist some scripts such as [hmi1.sh](deployments/hmi1.sh), [hmi2.sh](deployments/hmi2.sh) or [attacker.sh](deployments/attacker.sh) which can attach user to the container. 
### Run in GNS3
