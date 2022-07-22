class NetworkNode:
    def __init__(self, ip, mac):
        self.IP = ip
        self.MAC = mac

    def is_switch(self):
        return self.IP.split('.')[3] == '1'

    def __str__(self):
        return 'IP:{} MAC:{}'.format(self.IP, self.MAC)
