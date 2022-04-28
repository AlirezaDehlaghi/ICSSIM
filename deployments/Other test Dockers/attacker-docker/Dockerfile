FROM kalilinux/kali-rolling

RUN mkdir src


RUN apt-get update

RUN DEBIAN_FRONTEND="noninteractive" apt-get -y install tzdata

RUN apt-get install -y sudo \
&& apt-get install -y python3 \
&& apt-get install -y iputils-ping \
&& apt-get install -y net-tools \
&& apt-get install -y git \
&& apt-get -y install nano \
&& apt --yes install python3-pip \	
&& pip install pyModbusTCP \
&& apt install telnet \
&& apt-get install -y memcached \
&& apt-get install -y python3-memcache \ 
&& apt-get install -y ettercap-common 

WORKDIR /src

#memcached -d -u nobody memcached -l 127.0.0.1:11211,10.5.0.3


#COPY ./start.sh ./start.sh


