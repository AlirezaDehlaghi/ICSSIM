
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
#### Running the sample project 
Run the sample project using the prepared script **init.sh**
[enter link description here](deployments/)
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
### Run in GNS3
