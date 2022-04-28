FROM ubuntu:18.04
# COPY ./src .
COPY ./start.sh ./start.sh
RUN apt-get update
RUN apt-get install -y sudo \
    && apt-get install -y python2.7 \
    && apt-get install -y python-pip \
    && apt-get install -y iputils-ping \
    && apt-get install -y net-tools \
    && apt-get install -y git\
    && apt-get install -y screen\
    && git clone git://github.com/mininet/mininet \
    && /mininet/util/install.sh \
    && pip install minicps \
    && apt-get install -y ettercap-common \
    && chmod +x ./start.sh

