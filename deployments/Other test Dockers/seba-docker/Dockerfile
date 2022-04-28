FROM ubuntu:18.04
# COPY ./src .

RUN mkdir src

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    curl \
    iproute2 \
    iputils-ping \
    net-tools \
    iptables \
    python3 \
    python-pip \
    openvswitch-switch \
    openvswitch-testcontroller \
    tcpdump \
    vim \
    git \
    wireshark \
    x11-xserver-utils \
    xterm \
    hping3 \
    screen \
    mininet \
    build-essential python-dev libnetfilter-queue-dev \
    debhelper bison check cmake flex groff libbsd-dev \
    libcurl4-openssl-dev libgeoip-dev libgtk-3-dev libltdl-dev libluajit-5.1-dev \
    libncurses5-dev libnet1-dev libpcap-dev libpcre3-dev libssl-dev \
 && git clone https://github.com/Ettercap/ettercap.git \
 && pip install --upgrade setuptools \
 && pip install minicps \
 && pip install cpppo==4.1.0 \
 && pip install scapy \
 && pip install NetfilterQueue \
 && apt-get clean \
 && rm -rf /var/lib/apt 

RUN cd ettercap && mkdir build && cd build && cmake .. && make install
EXPOSE 6633 6653 6640


