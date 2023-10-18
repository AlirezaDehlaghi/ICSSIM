

printStep(){
    echo ""
    echo ""
    echo "[" $1 "STARTED]"
    sleep 1 
}

printStep 'DOCKER_COMPOSE UP'
sudo docker-compose up -d

printStep 'DOCKER_COMPOSE UP'
sudo docker-compose ps

sudo tcpdump -w traffic.pcap -i br_icsnet


