

printStep(){
    echo ""
    echo ""
    echo "[" $1 "STARTED]"
    sleep 1 
}

printStep "DOWN PREVIOUS CONTAINERS"
sudo docker-compose down 



