

printStep(){
    echo ""
    echo ""
    echo "[" $1 "STARTED]"
    sleep 1 
}

printStep "DEPLOYMENT"

printStep "DOWN PREVIOUS CONTAINERS"
sudo docker-compose down 

printStep "CTEATE TEMP SRC FILE"
mkdir ./ics-docker/src/ 
mkdir ./attacker-docker/src/ 

printStep "PRUNING DOCKER"
sudo docker system prune -f

printStep 'DOCKER_COMPOSE BUILD'
sudo docker-compose build

printStep "REMOVE TEMP SRC FILE"
rm -r ./ics-docker/src/ 
rm -r ./attacker-docker/src/ 

printStep 'DOCKER_COMPOSE UP'
sudo docker-compose up -d

printStep 'DOCKER_COMPOSE UP'
sudo docker-compose ps




