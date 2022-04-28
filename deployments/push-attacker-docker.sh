printStep(){
    echo ""
    echo ""
    echo "[" $1 "STARTED]"
    sleep 1 
}


name="$1"
if [ -z "$1" ]
then
      echo "need a name to push"
      exit 1
fi

printStep "COPY THE SOURCE CODE"
cp -R ./../src/ ./ics-docker/src/ 

printStep "BUILD DOCKER $1"
docker build --tag $1 ./ics-docker

printStep "TAG DOCKER alirezadehlaghi/$1"
docker tag $1 alirezadehlaghi/$1

printStep "PUSH DOCKER alirezadehlaghi/$1"
docker push alirezadehlaghi/$1

printStep "CLEANING THE STAGE"
rm -r ./ics-docker/src/
